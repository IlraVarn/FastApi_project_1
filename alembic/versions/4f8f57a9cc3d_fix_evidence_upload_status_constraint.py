"""fix evidence upload status constraint

Revision ID: 4f8f57a9cc3d
Revises: 156bcf420e54
Create Date: 2026-09-18 16:29:35.539228
"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "4f8f57a9cc3d"
down_revision: Union[str, Sequence[str], None] = "156bcf420e54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass