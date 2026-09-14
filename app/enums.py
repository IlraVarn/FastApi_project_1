from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum



class EvidenceUploadStatusType(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"



class GateStatusType(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"    


class GateType(str, Enum):
    COMMISSIONING_ACCEPTANCE = "commissioning_acceptance"
    CLOSEOUT_HANDOFF = "closeout_handoff"
    READINESS_REVIEW = "readiness_review"


class GateRequirementType(str, Enum):
    COMMISSIONING_REPORT = "commissioning_report"
    AS_BUILT_DRAWINGS = "as_built_drawings"
    O_AND_M_MANUALS = "o_and_m_manuals"
    TEST_RECORDS = "test_records"

