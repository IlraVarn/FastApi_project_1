"""correct evidence upload status constraint

Revision ID: 506011d17123
Revises: 4f8f57a9cc3d
Create Date: 2026-09-18 16:45:18.842350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '506011d17123'
down_revision: Union[str, Sequence[str], None] = '4f8f57a9cc3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_constraint(
        "ck_evidence_versions_upload_status_valid",
        "evidence_versions",
        type_="check",
    )

    op.create_check_constraint(
        "ck_evidence_versions_upload_status_valid",
        "evidence_versions",
        "upload_status IN ('pending', 'available')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_evidence_versions_upload_status_valid",
        "evidence_versions",
        type_="check",
    )

    op.execute(
    """
    UPDATE evidence_versions
    SET
        upload_status = 'pending',
        available_at = NULL
    WHERE upload_status = 'available'
    """
)
    op.create_check_constraint(
        "ck_evidence_versions_upload_status_valid",
        "evidence_versions",
        "upload_status IN ('pending', 'complete', 'failed')",
    )


