"""make workflowrecord.reference non nullable

Revision ID: 9fae45b335ef
Revises: d61d9d466ce0
Create Date: 2026-10-19 11:07:37.123671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '9fae45b335ef'
down_revision: Union[str, Sequence[str], None] = 'd61d9d466ce0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        """
        UPDATE workflow_records
        SET reference = 'Legacy workflow ' || id::text
        WHERE reference IS NULL
        """
    )

    op.alter_column(
        "workflow_records",
        "reference",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "workflow_records",
        "reference",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )