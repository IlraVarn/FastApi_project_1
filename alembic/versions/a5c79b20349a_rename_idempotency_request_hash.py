"""rename idempotency request hash

Revision ID: a5c79b20349a
Revises: d046e1dae623
Create Date: 2026-10-03 11:20:24.049054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'a5c79b20349a'
down_revision: Union[str, Sequence[str], None] = 'd046e1dae623'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "idempotency_records",
        "request_hash",
        new_column_name="idempotency_request_hash",
    )


def downgrade() -> None:
    op.alter_column(
        "idempotency_records",
        "idempotency_request_hash",
        new_column_name="request_hash",
    )