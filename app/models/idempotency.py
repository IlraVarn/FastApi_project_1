from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import CheckConstraint, Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel
from typing import Any
from sqlalchemy.dialects.postgresql import JSONB


#memory of which request created the evidenceversion
class IdempotencyRecord(SQLModel, table=True):
    __tablename__: ClassVar[str] = "idempotency_records"


    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "operation",
            "idempotency_key",
            name="uq_idempotency_org_operation_key",
        ), #Only the same organization + same operation + same idempotency key counts as a duplicate; 
        #the request hash does not decide uniqueness.
        CheckConstraint(
            "length(trim(operation)) > 0",
            name="ck_idempotency_operation_non_empty",
        ),
        CheckConstraint(
            "length(trim(idempotency_key)) > 0",
            name="ck_idempotency_key_non_empty",
        ),
        CheckConstraint(
            "length(request_hash) = 64",
            name="ck_idempotency_request_hash_length",
        ),
    )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    organization_id: int = Field(
        foreign_key="organizations.id",
        nullable=False,
    )

    operation: str = Field(
        nullable=False,
    )
    #"which attempted operation is this?"
    idempotency_key: str = Field(
        nullable=False,
    )
    #"what data did that operation contain?"
    idempotency_request_hash: str = Field(
        nullable=False,
    )

#     SHA-256 of the request data
#     proves whether a retry is the same request
    gate_id: int | None = Field(
        default=None,
        foreign_key="gates.id",
        nullable=True,
    )

    evidence_id: int | None = Field(
        default=None,
        foreign_key="evidence.id",
        nullable=True,
    )

    evidence_version_id: int | None = Field(
        default=None,
        foreign_key="evidence_versions.id",
        nullable=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )


# Idempotency-Key:
# "which attempted operation is this?"

# request_hash:
# "what data did that operation contain?"