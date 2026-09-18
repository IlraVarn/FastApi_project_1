"""add idempotency and evidence upload availability

Revision ID: b5a6a16d0b38
Revises: 092db7fb3d62
Create Date: 2026-09-18 14:44:25.947511
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "b5a6a16d0b38"
down_revision: Union[str, Sequence[str], None] = "092db7fb3d62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add idempotency records and verified EvidenceVersion availability state."""

    op.create_table(
        "idempotency_records",
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
            "operation",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "idempotency_key",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "request_hash",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "gate_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "evidence_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "evidence_version_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(request_hash) = 64",
            name="ck_idempotency_request_hash_length",
        ),
        sa.CheckConstraint(
            "length(trim(idempotency_key)) > 0",
            name="ck_idempotency_key_non_empty",
        ),
        sa.CheckConstraint(
            "length(trim(operation)) > 0",
            name="ck_idempotency_operation_non_empty",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["gate_id"],
            ["gates.id"],
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id"],
            ["evidence.id"],
        ),
        sa.ForeignKeyConstraint(
            ["evidence_version_id"],
            ["evidence_versions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "operation",
            "idempotency_key",
            name="uq_idempotency_org_operation_key",
        ),
    )

    op.add_column(
        "evidence_versions",
        sa.Column(
            "available_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.alter_column(
        "evidence_versions",
        "checksum_sha256",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )

    # Replace the old:
    # pending / complete / failed
    #
    # with the current:
    # pending / available
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

    op.create_check_constraint(
        "ck_evidence_versions_checksum_sha256_length",
        "evidence_versions",
        "length(checksum_sha256) = 64",
    )

    op.create_check_constraint(
        "ck_evidence_versions_storage_key_non_empty",
        "evidence_versions",
        "length(trim(storage_key)) > 0",
    )

    op.create_check_constraint(
        "ck_evidence_versions_available_state_valid",
        "evidence_versions",
        """
        (
            upload_status = 'available'
            AND available_at IS NOT NULL
        )
        OR
        (
            upload_status = 'pending'
            AND available_at IS NULL
        )
        """,
    )


def downgrade() -> None:
    """Restore the schema from revision 092db7fb3d62."""

    op.drop_constraint(
        "ck_evidence_versions_available_state_valid",
        "evidence_versions",
        type_="check",
    )

    op.drop_constraint(
        "ck_evidence_versions_storage_key_non_empty",
        "evidence_versions",
        type_="check",
    )

    op.drop_constraint(
        "ck_evidence_versions_checksum_sha256_length",
        "evidence_versions",
        type_="check",
    )

    op.drop_constraint(
        "ck_evidence_versions_upload_status_valid",
        "evidence_versions",
        type_="check",
    )

    # Convert the new name back to the old schema's name
    # before reinstating the old CHECK constraint.
    op.execute(
        """
        UPDATE evidence_versions
        SET upload_status = 'complete'
        WHERE upload_status = 'available'
        """
    )

    op.create_check_constraint(
        "ck_evidence_versions_upload_status_valid",
        "evidence_versions",
        "upload_status IN ('pending', 'complete', 'failed')",
    )

    op.alter_column(
        "evidence_versions",
        "checksum_sha256",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )

    op.drop_column(
        "evidence_versions",
        "available_at",
    )

    op.drop_table(
        "idempotency_records",
    )