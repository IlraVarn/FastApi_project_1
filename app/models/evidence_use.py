
from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum



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

