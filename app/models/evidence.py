from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum
from app.enums import EvidenceUploadStatusType

class Evidence(SQLModel, table = True):
    __tablename__: ClassVar[str] = "evidence"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0", 
            name="ck_evidence_name_non_empty"),
        )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    organization_id: int = Field(
        foreign_key="organizations.id",
        nullable=False,
        index=True,
    )
    name: str = Field(
        nullable=False 
    )


class EvidenceVersion(SQLModel, table=True):
    __tablename__: ClassVar[str] = "evidence_versions"

    __table_args__ = (
        CheckConstraint( 
            "version_number > 0", 
            name="ck_evidence_versions_version_positive",
        ),
        CheckConstraint(
            "size_bytes > 0",
            name="ck_evidence_versions_size_positive",
        ),
        CheckConstraint(
            "upload_status IN ('pending', 'available')",
            name="ck_evidence_versions_upload_status_valid",
        ),
        CheckConstraint(
            "length(trim(original_filename)) > 0",
            name="ck_evidence_versions_filename_non_empty",
        ),
        CheckConstraint( 
            "length(trim(content_type)) > 0", 
            name="ck_evidence_versions_content_type_non_empty", 
        ), 
        UniqueConstraint( 
                "evidence_id", "version_number", 
                name="uq_evidence_versions_evidence_version", 
        ),
        UniqueConstraint(
            "storage_key",
            name="uq_evidence_versions_storage_key",
        ),
        CheckConstraint(
            "length(trim(storage_key)) > 0",
            name="ck_evidence_versions_storage_key_non_empty",
        ),
        CheckConstraint(
            "length(checksum_sha256) = 64",
            name="ck_evidence_versions_checksum_sha256_length",
        ),
        CheckConstraint(
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
            name="ck_evidence_versions_available_state_valid",
        ),
        )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    evidence_id: int = Field(
        foreign_key="evidence.id",
        nullable=False,
    )

    version_number: int = Field(nullable=False)

    storage_key: str = Field(nullable=False)

    original_filename: str = Field(nullable=False)

    content_type: str = Field(nullable=False)

    size_bytes: int = Field(nullable=False)

    checksum_sha256: str = Field(
        nullable=False,
    )

    upload_status: str = Field(
        default=EvidenceUploadStatusType.PENDING.value,
        nullable=False,
    )
    created_by_user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

    available_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
    )


    