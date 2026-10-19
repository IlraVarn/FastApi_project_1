from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum
from app.enums import GateType, GateStatusType




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

    gate_submission_id: int | None = Field(
        default=None,
        foreign_key="gate_submissions.id",
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

    authorization_role: str | None = Field(
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

