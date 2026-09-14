from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum

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
            "upload_status IN ('pending', 'complete', 'failed')",
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

    checksum_sha256: str | None = Field(
        default=None,
        nullable=True,
    )

    upload_status: str = Field(
        default="pending",
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

