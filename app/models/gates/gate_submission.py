from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, UTC
from typing import ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime




class GateSubmission(SQLModel, table=True):
    __tablename__: ClassVar[str] = "gate_submissions"

    __table_args__ = (
        CheckConstraint(
            "submission_number > 0",
            name="ck_gate_submission_number_positive",
        ),
        UniqueConstraint(
            "gate_id",
            "submission_number",
            name="uq_gate_submission_gate_number",
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

    submission_number: int = Field(
        nullable=False,
    )

    submitted_by_user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )

    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )


class GateSubmissionEvidence(SQLModel, table=True):
    __tablename__: ClassVar[str] = "gate_submission_evidence"

    gate_submission_id: int = Field(
        foreign_key="gate_submissions.id",
        primary_key=True,
    )

    gate_requirement_id: int = Field(
        foreign_key="gate_requirements.id",
        primary_key=True,
    )

    evidence_version_id: int = Field(
        foreign_key="evidence_versions.id",
        primary_key=True,
        index=True,
    )

