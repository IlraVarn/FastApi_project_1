from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, UTC
from typing import ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum

class User(SQLModel, table=True):
    __tablename__: ClassVar[str] = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email",),
        CheckConstraint("length(trim(name)) > 0", name="ck_user_name_non_empty"),
        CheckConstraint("length(trim(email)) > 0", name="ck_user_email_non_empty"),
        )
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False)
    )
    archived_at: datetime | None = Field(
        default=None, 
        sa_column=Column(
            DateTime(timezone=True),
        nullable=True)
    )

