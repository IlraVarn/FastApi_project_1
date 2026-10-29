from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum
from app.enums import GateType, GateRequirementType, GateStatusType



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
    expected_row_version: int = Field(gt=0)

class GateRequirementPublic(SQLModel):
    id: int
    requirement_type: GateRequirementType
    created_at: datetime


class GatePublic(SQLModel):
    id: int
    organization_id: int
    created_by_user_id: int
    gate_type: str
    status: GateStatusType
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    reference: str | None
    row_version: int


class GateListPublicWithCount(SQLModel):
    data: list[GatePublic]
    count: int


class GateWithRequirementsPublic(GatePublic):
    requirements: list[GateRequirementPublic]


class GateStateTransitionRequest(SQLModel):
    target_status: GateStatusType
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


#example response:
# gate_response = GateWithRequirementsPublic(
#     id=10,
#     organization_id=7,
#     gate_type="commissioning_acceptance",
#     status=GateStatusType.DRAFT,
#     created_at=datetime(2026, 9, 14, 16, 0, tzinfo=UTC),
#     updated_at=datetime(2026, 9, 14, 16, 0, tzinfo=UTC),
#     archived_at=None,
#     reference="Project A",
#     requirements=[
#         GateRequirementPublic(
#             id=51,
#             requirement_type=GateRequirementType.COMMISSIONING_REPORT,
#             created_at=datetime(2026, 9, 14, 16, 0, tzinfo=UTC),
#         ),
#         GateRequirementPublic(
#             id=52,
#             requirement_type=GateRequirementType.TEST_RECORDS,
#             created_at=datetime(2026, 9, 14, 16, 0, tzinfo=UTC),
#         ),
#     ],
# )