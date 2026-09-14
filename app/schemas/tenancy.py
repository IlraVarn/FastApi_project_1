from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum


#ORGANIZATIONS



class OrganizationCreate(SQLModel):
    name: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value
    

class OrganizationPublic(SQLModel):
    id: int
    name: str


#MEMBERSHIPS

class MembershipPublic(SQLModel):
    id: int
    user_id: int
    organization_id: int
    status: Literal["active", "inactive"]

