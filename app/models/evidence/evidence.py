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
            name="ck_evidence_versions_size_positive"
            ),
        CheckConstraint(
            "size_bytes <= 26214400",
            name="ck_evidence_versions_size_max",
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
        ), #same Evidence cannot have the same version number twice
        
        UniqueConstraint(
            "storage_key",
            name="uq_evidence_versions_storage_key",
        ), #Two EvidenceVersions cannot point to the exact same S3 object location

        CheckConstraint(
            "length(trim(storage_key)) > 0",
            name="ck_evidence_versions_storage_key_non_empty",
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
        CheckConstraint(
            "checksum_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_evidence_versions_checksum_sha256_hex",
        )
        )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    evidence_id: int = Field(
        foreign_key="evidence.id",
        nullable=False,
    )
    #historical version of evidence
    version_number: int = Field(nullable=False)

    #proves where the file is. 
    # An object inside S3 bucket. Backend builds it.
    storage_key: str = Field(nullable=False)

    original_filename: str = Field(nullable=False)

    content_type: str = Field(nullable=False)

    size_bytes: int = Field(nullable=False)

    #fingerprint of file's bytes. Proves it's the same file
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


# Very important separation:
# checksum
# =
# byte integrity

# file-type validation
# =
# what kind of file is this?

# malware scan
# =
# does it contain known malicious content?

# business validation
# =
# does this evidence satisfy the requirement?
# Do not collapse those into one concept.

    

# Example storage key:

# organizations/1/evidence/3/versions/2/e5149b846dee4dc696ded7d27b40f0f3

# Example presigned URL:

# https://your-bucket.s3.us-west-2.amazonaws.com/
# organizations/1/evidence/3/versions/2/e5149b...
# ?X-Amz-Algorithm=...
# &X-Amz-Signature=...


# Relationship:

# storage_key
# ↓
# passed into create_presigned_upload()
# ↓
# AWS builds a temporary signed URL for that exact key
# ↓
# browser receives the URL
# ↓
# browser PUTs file bytes to that URL