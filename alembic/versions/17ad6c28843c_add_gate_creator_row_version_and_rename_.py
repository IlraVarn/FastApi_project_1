"""add gate creator row version and rename workflow record name

Revision ID: 17ad6c28843c
Revises: 9fae45b335ef
Create Date: 2026-10-29 11:10:11.002337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '17ad6c28843c'
down_revision: Union[str, Sequence[str], None] = '9fae45b335ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename WorkflowRecord.reference -> name.
    # Preserve all existing values.
    op.alter_column(
        "workflow_records",
        "reference",
        new_column_name="name",
        existing_type=sa.VARCHAR(),
        existing_nullable=False,
    )

    # 2. Add Gate.created_by_user_id temporarily nullable
    # because existing Gate rows do not have a value yet.
    op.add_column(
        "gates",
        sa.Column(
            "created_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Backfill existing Gates.
    # Prefer the earliest known Gate transition actor.
    # Otherwise use an active member of that organization.
    op.execute(
        """
        UPDATE gates AS g
        SET created_by_user_id = COALESCE(
            (
                SELECT gst.actor_user_id
                FROM gate_state_transitions AS gst
                WHERE gst.gate_id = g.id
                ORDER BY gst.occurred_at ASC, gst.id ASC
                LIMIT 1
            ),
            (
                SELECT m.user_id
                FROM memberships AS m
                WHERE m.organization_id = g.organization_id
                  AND m.status = 'active'
                ORDER BY
                    CASE WHEN m.role = 'admin' THEN 0 ELSE 1 END,
                    m.id ASC
                LIMIT 1
            )
        )
        WHERE g.created_by_user_id IS NULL
        """
    )

    # Fail instead of silently leaving invalid rows.
    connection = op.get_bind()

    missing_creator_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM gates
            WHERE created_by_user_id IS NULL
            """
        )
    ).scalar_one()

    if missing_creator_count != 0:
        raise RuntimeError(
            "Cannot backfill created_by_user_id for all existing Gates"
        )

    # Now enforce NOT NULL.
    op.alter_column(
        "gates",
        "created_by_user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        "ix_gates_created_by_user_id",
        "gates",
        ["created_by_user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_gates_created_by_user_id",
        "gates",
        "users",
        ["created_by_user_id"],
        ["id"],
    )

    # 3. Add row_version.
    # Existing Gates all begin at version 1.
    op.add_column(
        "gates",
        sa.Column(
            "row_version",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE gates
        SET row_version = 1
        WHERE row_version IS NULL
        """
    )

    op.alter_column(
        "gates",
        "row_version",
        existing_type=sa.Integer(),
        nullable=False,
    )

def downgrade() -> None:
    op.drop_column(
        "gates",
        "row_version",
    )

    op.drop_constraint(
        "fk_gates_created_by_user_id",
        "gates",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_gates_created_by_user_id",
        table_name="gates",
    )

    op.drop_column(
        "gates",
        "created_by_user_id",
    )

    op.alter_column(
        "workflow_records",
        "name",
        new_column_name="reference",
        existing_type=sa.VARCHAR(),
        existing_nullable=False,
    )