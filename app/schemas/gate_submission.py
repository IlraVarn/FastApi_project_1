from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum
from app.enums import GateType, GateRequirementType, GateStatusType




class GateSubmissionCreateRequest(SQLModel):
    expected_row_version: int = Field(gt=0)


class GateSubmissionPublic(SQLModel):
    id: int
    gate_id: int
    submission_numer: int
    submitted_by_user_id: int
    submitted_at: datetime

