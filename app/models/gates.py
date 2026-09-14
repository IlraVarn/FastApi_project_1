from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum
from app.enums import GateType, GateStatusType



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

    status: str = Field(default=GateStatusType.DRAFT.value,
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

