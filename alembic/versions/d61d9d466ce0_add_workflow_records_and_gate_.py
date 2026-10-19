"""add workflow records and gate submissions

Revision ID: d61d9d466ce0
Revises: 48ac0eda017b
Create Date: 2026-10-19 10:47:13.632684
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "d61d9d466ce0"
down_revision: Union[str, Sequence[str], None] = "48ac0eda017b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema while preserving existing test data."""

    # ---------------------------------------------------------
    # 1. Create workflow_records
    # ---------------------------------------------------------

    op.create_table(
        "workflow_records",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "created_by_user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "reference",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "archived_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
        ),

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),

        sa.UniqueConstraint(
            "id",
            "organization_id",
            name="uq_workflow_record_id_organization",
        ),
    )

    op.create_index(
        op.f("ix_workflow_records_created_by_user_id"),
        "workflow_records",
        ["created_by_user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_records_organization_id"),
        "workflow_records",
        ["organization_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 2. Backfill one WorkflowRecord for every existing Gate.
    #
    # Existing Gates did not previously have WorkflowRecords.
    # One-per-Gate is the safest migration because it does not
    # invent relationships between unrelated existing Gates.
    #
    # Existing Gate.id is reused as the migration-created
    # WorkflowRecord.id so the mapping is deterministic.
    #
    # created_by_user_id is derived from:
    #   1. earliest GateStateTransition actor, if one exists
    #   2. active organization Membership
    #   3. any organization Membership
    # ---------------------------------------------------------

    connection = op.get_bind()

    missing_creator_gate_ids = connection.execute(
        sa.text(
            """
            SELECT g.id
            FROM gates AS g
            WHERE NOT EXISTS (
                SELECT 1
                FROM gate_state_transitions AS gst
                WHERE gst.gate_id = g.id
            )
            AND NOT EXISTS (
                SELECT 1
                FROM memberships AS m
                WHERE m.organization_id = g.organization_id
            )
            """
        )
    ).scalars().all()

    if missing_creator_gate_ids:
        raise RuntimeError(
            "Cannot backfill WorkflowRecord.created_by_user_id "
            "for existing Gate IDs: "
            f"{missing_creator_gate_ids}"
        )

    op.execute(
        """
        INSERT INTO workflow_records (
            id,
            organization_id,
            created_by_user_id,
            reference,
            created_at,
            updated_at,
            archived_at
        )
        SELECT
            g.id,
            g.organization_id,

            COALESCE(
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
                        CASE
                            WHEN m.role = 'admin' THEN 0
                            ELSE 1
                        END,
                        m.id ASC
                    LIMIT 1
                ),
                (
                    SELECT m.user_id
                    FROM memberships AS m
                    WHERE m.organization_id = g.organization_id
                    ORDER BY m.id ASC
                    LIMIT 1
                )
            ),

            g.reference,
            g.created_at,
            g.updated_at,
            g.archived_at

        FROM gates AS g
        """
    )

    # Because migration-created WorkflowRecord IDs were explicitly
    # copied from Gate IDs, advance the PostgreSQL sequence so future
    # normal inserts do not collide with those IDs.

    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence(
                'workflow_records',
                'id'
            ),
            COALESCE(
                (
                    SELECT MAX(id)
                    FROM workflow_records
                ),
                1
            ),
            EXISTS (
                SELECT 1
                FROM workflow_records
            )
        )
        """
    )

    # ---------------------------------------------------------
    # 3. Create GateSubmission
    # ---------------------------------------------------------

    op.create_table(
        "gate_submissions",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "gate_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "submission_number",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "submitted_by_user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.CheckConstraint(
            "submission_number > 0",
            name="ck_gate_submission_number_positive",
        ),

        sa.ForeignKeyConstraint(
            ["gate_id"],
            ["gates.id"],
        ),

        sa.ForeignKeyConstraint(
            ["submitted_by_user_id"],
            ["users.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),

        sa.UniqueConstraint(
            "gate_id",
            "submission_number",
            name="uq_gate_submission_gate_number",
        ),
    )

    op.create_index(
        op.f("ix_gate_submissions_gate_id"),
        "gate_submissions",
        ["gate_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_gate_submissions_submitted_by_user_id"),
        "gate_submissions",
        ["submitted_by_user_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 4. Create GateSubmissionEvidence
    # ---------------------------------------------------------

    op.create_table(
        "gate_submission_evidence",

        sa.Column(
            "gate_submission_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "gate_requirement_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "evidence_version_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["evidence_version_id"],
            ["evidence_versions.id"],
        ),

        sa.ForeignKeyConstraint(
            ["gate_requirement_id"],
            ["gate_requirements.id"],
        ),

        sa.ForeignKeyConstraint(
            ["gate_submission_id"],
            ["gate_submissions.id"],
        ),

        sa.PrimaryKeyConstraint(
            "gate_submission_id",
            "gate_requirement_id",
            "evidence_version_id",
        ),
    )

    op.create_index(
        op.f(
            "ix_gate_submission_evidence_evidence_version_id"
        ),
        "gate_submission_evidence",
        ["evidence_version_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 5. Add EvidenceUse audit fields.
    #
    # Add nullable FIRST because existing rows do not yet have
    # values.
    # ---------------------------------------------------------

    op.add_column(
        "evidence_uses",
        sa.Column(
            "created_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "evidence_uses",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Historical EvidenceUse creator/time were never stored.
    #
    # For existing TEST rows, use the linked EvidenceVersion's
    # creator/time as deterministic legacy backfill values.

    op.execute(
        """
        UPDATE evidence_uses AS eu
        SET
            created_by_user_id = ev.created_by_user_id,
            created_at = ev.created_at
        FROM evidence_versions AS ev
        WHERE ev.id = eu.evidence_version_id
        """
    )

    # Make sure the backfill succeeded before enforcing NOT NULL.

    remaining_evidence_uses = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM evidence_uses
            WHERE created_by_user_id IS NULL
               OR created_at IS NULL
            """
        )
    ).scalar_one()

    if remaining_evidence_uses != 0:
        raise RuntimeError(
            "EvidenceUse audit backfill failed for "
            f"{remaining_evidence_uses} row(s)"
        )

    op.alter_column(
        "evidence_uses",
        "created_by_user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "evidence_uses",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.create_foreign_key(
        "fk_evidence_uses_created_by_user_id",
        "evidence_uses",
        "users",
        ["created_by_user_id"],
        ["id"],
    )

    # ---------------------------------------------------------
    # 6. Extend GateStateTransition
    # ---------------------------------------------------------

    op.add_column(
        "gate_state_transitions",
        sa.Column(
            "gate_submission_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "gate_state_transitions",
        sa.Column(
            "authorization_role",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f(
            "ix_gate_state_transitions_gate_submission_id"
        ),
        "gate_state_transitions",
        ["gate_submission_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_gate_state_transitions_gate_submission_id",
        "gate_state_transitions",
        "gate_submissions",
        ["gate_submission_id"],
        ["id"],
    )

    # ---------------------------------------------------------
    # 7. Add Gate.workflow_record_id.
    #
    # Nullable FIRST so existing Gates survive.
    # ---------------------------------------------------------

    op.add_column(
        "gates",
        sa.Column(
            "workflow_record_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Each existing Gate gets the migration-created WorkflowRecord
    # having the same ID.

    op.execute(
        """
        UPDATE gates
        SET workflow_record_id = id
        """
    )

    remaining_gates = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM gates
            WHERE workflow_record_id IS NULL
            """
        )
    ).scalar_one()

    if remaining_gates != 0:
        raise RuntimeError(
            "Gate WorkflowRecord backfill failed for "
            f"{remaining_gates} row(s)"
        )

    # Now enforce the final NOT NULL model.

    op.alter_column(
        "gates",
        "workflow_record_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        op.f("ix_gates_workflow_record_id"),
        "gates",
        ["workflow_record_id"],
        unique=False,
    )

    # Remove old direct Gate → Organization FK.

    op.drop_constraint(
        op.f("gates_organization_id_fkey"),
        "gates",
        type_="foreignkey",
    )

    # Replace it with the stronger pair:
    #
    # Gate.workflow_record_id
    # +
    # Gate.organization_id
    #
    # must match the same WorkflowRecord row.

    op.create_foreign_key(
        "fk_gate_workflow_record_organization",
        "gates",
        "workflow_records",
        [
            "workflow_record_id",
            "organization_id",
        ],
        [
            "id",
            "organization_id",
        ],
    )

    # ---------------------------------------------------------
    # 8. Rename Organization.name
    # ---------------------------------------------------------

    op.alter_column(
        "organizations",
        "name",
        new_column_name="organization_name",
        existing_type=sa.VARCHAR(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema while preserving original tables."""

    # ---------------------------------------------------------
    # Organization
    # ---------------------------------------------------------

    op.alter_column(
        "organizations",
        "organization_name",
        new_column_name="name",
        existing_type=sa.VARCHAR(),
        existing_nullable=False,
    )

    # ---------------------------------------------------------
    # Gate
    # ---------------------------------------------------------

    op.drop_constraint(
        "fk_gate_workflow_record_organization",
        "gates",
        type_="foreignkey",
    )

    op.create_foreign_key(
        op.f("gates_organization_id_fkey"),
        "gates",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    op.drop_index(
        op.f("ix_gates_workflow_record_id"),
        table_name="gates",
    )

    op.drop_column(
        "gates",
        "workflow_record_id",
    )

    # ---------------------------------------------------------
    # GateStateTransition
    # ---------------------------------------------------------

    op.drop_constraint(
        "fk_gate_state_transitions_gate_submission_id",
        "gate_state_transitions",
        type_="foreignkey",
    )

    op.drop_index(
        op.f(
            "ix_gate_state_transitions_gate_submission_id"
        ),
        table_name="gate_state_transitions",
    )

    op.drop_column(
        "gate_state_transitions",
        "authorization_role",
    )

    op.drop_column(
        "gate_state_transitions",
        "gate_submission_id",
    )

    # ---------------------------------------------------------
    # EvidenceUse
    # ---------------------------------------------------------

    op.drop_constraint(
        "fk_evidence_uses_created_by_user_id",
        "evidence_uses",
        type_="foreignkey",
    )

    op.drop_column(
        "evidence_uses",
        "created_at",
    )

    op.drop_column(
        "evidence_uses",
        "created_by_user_id",
    )

    # ---------------------------------------------------------
    # GateSubmissionEvidence
    # ---------------------------------------------------------

    op.drop_index(
        op.f(
            "ix_gate_submission_evidence_evidence_version_id"
        ),
        table_name="gate_submission_evidence",
    )

    op.drop_table(
        "gate_submission_evidence",
    )

    # ---------------------------------------------------------
    # GateSubmission
    # ---------------------------------------------------------

    op.drop_index(
        op.f("ix_gate_submissions_submitted_by_user_id"),
        table_name="gate_submissions",
    )

    op.drop_index(
        op.f("ix_gate_submissions_gate_id"),
        table_name="gate_submissions",
    )

    op.drop_table(
        "gate_submissions",
    )

    # ---------------------------------------------------------
    # WorkflowRecord
    # ---------------------------------------------------------

    op.drop_index(
        op.f("ix_workflow_records_organization_id"),
        table_name="workflow_records",
    )

    op.drop_index(
        op.f("ix_workflow_records_created_by_user_id"),
        table_name="workflow_records",
    )

    op.drop_table(
        "workflow_records",
    )