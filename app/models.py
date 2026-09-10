from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum


# User
# UserPublic

# Organization
# OrganizationCreate
# OrganizationPublic

# Membership
# MembershipPublic

# EvidenceUploadStatus(str, Enum)
# Evidence
# EvidenceVersion
# EvidenceCreate
# EvidenceVersionCreate
# EvidencePublic
# EvidenceVersionPublic
# EvidenceCreatedPublic

# EvidenceUse

# GateStatus
# GateType
# Gate
# GateCreateRequest
# GatePatchRequesr
# GatePublic
# GateListPublicWithCount
# GateWithRequirementsPublic(GatePublic)


# GateRequirementType
# GateRequirement
# GateRequirementPublic


# GateStateTransition
# GateStateTransitionRequest

#USERS
class User(SQLModel, table=True):
    __tablename__: ClassVar[str] = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email",),
        CheckConstraint("length(trim(name)) > 0", name="ck_user_name_non_empty"),
        CheckConstraint("length(trim(email)) > 0", name="ck_user_email_non_empty"),
        )
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False)
    )
    archived_at: datetime | None = Field(
        default=None, 
        sa_column=Column(
            DateTime(timezone=True),
        nullable=True)
    )


class UserPublic(SQLModel):
    id: int
    name: str
    email: str


#ORGANIZATIONS
class Organization(SQLModel, table=True):
    __tablename__: ClassVar[str] = "organizations"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_organization_name_non_empty"),
        )
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)


class OrganizationCreate(SQLModel):
    name: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value
    

class OrganizationPublic(SQLModel):
    id: int
    name: str


#MEMBERSHIPS
class Membership(SQLModel, table=True):
    __tablename__: ClassVar[str] = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_memberships_user_organization",),
        CheckConstraint("status IN ('active', 'inactive')", name="ck_membership_status_valid"),
        CheckConstraint("role IN ('admin', 'member')",name="ck_membership_role_valid",)
        )
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False, foreign_key='users.id', index=True)
    organization_id: int = Field(nullable=False, foreign_key='organizations.id', index=True)
    status: str = Field(default='active', nullable=False)
    role: str = Field(default="member",nullable=False)


class MembershipPublic(SQLModel):
    id: int
    user_id: int
    organization_id: int
    status: Literal["active", "inactive"]


#EVIDENCE
class EvidenceUploadStatus(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"


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


class EvidenceCreate(SQLModel):
    model_config = ConfigDict(
        extra="forbid",
    )  # type: ignore[assignment]

    name: str = Field(
        min_length=1,
    )

    version: EvidenceVersionCreate

    @field_validator("name")
    @classmethod
    def strip_and_reject_blank(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value


class EvidenceVersionCreate(SQLModel):
    model_config = ConfigDict(
        extra="forbid",
    )  # type: ignore[assignment]

    original_filename: str = Field(
        min_length=1,
    )

    content_type: str = Field(
        min_length=1,
    )

    size_bytes: int = Field(
        gt=0,
    )

    @field_validator(
        "original_filename",
        "content_type",
    )
    @classmethod
    def strip_and_reject_blank(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value


class EvidencePublic(SQLModel):
    id: int
    name: str
    organization_id: int


class EvidenceVersionPublic(SQLModel):
    id: int
    evidence_id: int
    version_number: int
    original_filename: str
    content_type: str
    size_bytes: int
    checksum_sha256: str | None
    upload_status: EvidenceUploadStatus
    created_by_user_id: int
    created_at: datetime


class EvidenceCreatedPublic(SQLModel):
    evidence: EvidencePublic
    version: EvidenceVersionPublic


#EVIDENCEUSE
class EvidenceUse(SQLModel, table=True):
    __tablename__: ClassVar[str] = "evidence_uses"

    gate_requirement_id: int = Field(
        foreign_key="gate_requirements.id",
        primary_key=True,
    )

    evidence_version_id: int = Field(
        foreign_key="evidence_versions.id",
        primary_key=True,
        index=True,
    )


#GATES
class GateStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"    


class GateType(str, Enum):
    COMMISSIONING_ACCEPTANCE = "commissioning_acceptance"
    CLOSEOUT_HANDOFF = "closeout_handoff"
    READINESS_REVIEW = "readiness_review"


class Gate(SQLModel, table=True):
    __tablename__: ClassVar[str] = "gates"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'submitted', 'approved', 'rejected')", 
                        name="ck_gate_status_valid"),
        CheckConstraint(
            """
            gate_type IN (
                'commissioning_acceptance',
                'closeout_handoff',
                'readiness_review'
            )
            """,
            name="ck_gate_type_valid",
        ),
    )
    
    id: int | None = Field(default=None, primary_key=True)    

    organization_id: int = Field(
        nullable=False, 
        foreign_key='organizations.id',
        index=True)

    gate_type: str = Field(nullable=False)

    status: str = Field(default=GateStatus.DRAFT.value,
                        nullable=False)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False))

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,))
    
    #archived_at controls lyfecycle state so nullable makes it excplicit. 
    #i.e. archived_at is None => active order. Not none => archived order
    archived_at: datetime | None = Field(
        default=None, 
        sa_column=Column(
            DateTime(timezone=True),
        nullable=True)
    )
    reference: str | None = Field(default=None, nullable=True)


class GateCreateRequest(SQLModel):
    gate_type: GateType
    requirement_types: list[GateRequirementType] = Field(
        min_length=1,
    )


class GatePatchRequest(SQLModel):
    #extra= forbid sends back 422 if clent sends additional field.
    #rejects fields the client cannot mutate
    model_config = ConfigDict(extra='forbid') #type: ignore[assignment]
    reference: str | None = Field(default=None, min_length=1)


class GatePublic(SQLModel):
    id: int
    organization_id: int
    gate_type: str
    status: GateStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    reference: str | None


class GateListPublicWithCount(SQLModel):
    data: list[GatePublic]
    count: int


class GateWithRequirementsPublic(GatePublic):
    requirements: list[GateRequirementPublic]


#GATE REQUIREMENTs (instead of OrderItems)
class GateRequirementType(str, Enum):
    COMMISSIONING_REPORT = "commissioning_report"
    AS_BUILT_DRAWINGS = "as_built_drawings"
    O_AND_M_MANUALS = "o_and_m_manuals"
    TEST_RECORDS = "test_records"


class GateRequirement(SQLModel, table=True):
    __tablename__: ClassVar[str] = "gate_requirements"

    __table_args__ = (
        CheckConstraint(
        """
        requirement_type IN (
            'commissioning_report',
            'as_built_drawings',
            'o_and_m_manuals',
            'test_records'
        )
        """,
        name="ck_gate_requirement_type_valid",
    ),
    UniqueConstraint(
        "gate_id",
        "requirement_type",
        name="uq_gate_requirement_gate_type",
    ),
)
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    gate_id: int = Field(
        foreign_key="gates.id",
        nullable=False,
        index=True,
    )

    requirement_type: str = Field(
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )


class GateRequirementPublic(SQLModel):
    id: int
    requirement_type: GateRequirementType
    created_at: datetime


#GATE STATE TRANSITIONS
class GateStateTransition(SQLModel, table=True):
    __tablename__: ClassVar[str] = "gate_state_transitions"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    gate_id: int = Field(
        foreign_key="gates.id",
        nullable=False,
        index=True,
    )

    actor_user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )

    previous_status: str = Field(nullable=False)

    new_status: str = Field(nullable=False)

    reason: str | None = Field(
        default=None,
        nullable=True,
    )

    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )


class GateStateTransitionRequest(SQLModel):
    target_status: GateStatus
    reason: str | None = None

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if value == "":
            return None

        return value


#GATES SORT

GateSortBy = Literal["created_at", "status", "id"]
GateSortDirection = Literal["asc", "desc"]


GATE_SORT_COLUMNS = {
    "created_at": Gate.created_at,
    "status": Gate.status,
    "id": Gate.id,
}


