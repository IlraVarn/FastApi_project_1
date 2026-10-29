from __future__ import annotations
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC
from typing import  ClassVar, Any, cast
from sqlalchemy import (
    CheckConstraint, 
    UniqueConstraint, 
    Column, 
    DateTime,
    ForeignKeyConstraint,
    Table
)
from app.enums import GateStatusType
from sqlalchemy.orm import declared_attr



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
        ForeignKeyConstraint(
            ["workflow_record_id", "organization_id"],
            [
                "workflow_records.id",
                "workflow_records.organization_id",
            ],
            name="fk_gate_workflow_record_organization",
        ),
    )


    
    id: int | None = Field(default=None, primary_key=True)    

    organization_id: int = Field(
        nullable=False, 
        index=True)
    
    workflow_record_id: int = Field(
        nullable=False,
        index=True,
    )

    created_by_user_id: int = Field(
    foreign_key="users.id",
    nullable=False,
    index=True,
)

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

    row_version: int = Field(
        default=1,
        nullable=False,
    )

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

