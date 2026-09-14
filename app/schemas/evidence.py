
from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum
from app.enums import EvidenceUploadStatusType



class EvidenceVersionCreate(SQLModel):
    model_config = ConfigDict(extra="forbid",
                              )  # type: ignore[assignment]

    original_filename: str = Field(min_length=1)

    content_type: str = Field(min_length=1)

    size_bytes: int = Field(gt=0,le=26_214_400)


    @field_validator(
        "original_filename",
        "content_type",
    )
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value


class EvidenceCreate(SQLModel):
    model_config = ConfigDict(
        extra="forbid",
    )  # type: ignore[assignment]

    name: str = Field(min_length=1)

    version: EvidenceVersionCreate

    @field_validator("name")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
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
    upload_status: EvidenceUploadStatusType
    created_by_user_id: int
    created_at: datetime


class EvidenceCreatedPublic(SQLModel):
    evidence: EvidencePublic
    version: EvidenceVersionPublic




#     example:
# evidence_response = 
#     EvidenceCreatedPublic(
    #     evidence=EvidencePublic(
    #         id=30,
    #         organization_id=10,
    #         name="Calibration Certificate",
    #     ),
    #     version=EvidenceVersionPublic(
    #         id=81,
    #         evidence_id=30,
    #         version_number=1,
    #         original_filename="certificate.pdf",
    #         content_type="application/pdf",
    #         size_bytes=230000,
    #         checksum_sha256=None,
    #         upload_status="pending",
    #         created_by_user_id=7,
    #         created_at=...,
    #     ),
# )