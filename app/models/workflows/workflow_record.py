# app/models/workflows/workflow_record.py

from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

#child of Organization, parent of Gate
class WorkflowRecord(SQLModel, table=True):
    __tablename__: ClassVar[str] = "workflow_records"

    __table_args__ = (
        UniqueConstraint(
            "id",
            "organization_id",
            name="uq_workflow_record_id_organization",
        ),
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

    created_by_user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )

    name: str = Field(
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

    archived_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
    )