from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum

class Organization(SQLModel, table=True):
    __tablename__: ClassVar[str] = "organizations"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_organization_name_non_empty"),
        )
    
    id: int | None = Field(default=None, primary_key=True)
    organization_name: str = Field(nullable=False)


class Membership(SQLModel, table=True):
    __tablename__: ClassVar[str] = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_memberships_user_organization",),
        CheckConstraint("status IN ('active', 'inactive')", name="ck_membership_status_valid"),
        CheckConstraint("role IN ('admin', 'member')",name="ck_membership_role_valid",)
        )
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False, foreign_key='users.id', index=True)
    organization_id: int = Field(nullable=False, foreign_key='organizations.id', index=True)
    status: str = Field(default='active', nullable=False)
    role: str = Field(default="member",nullable=False)

