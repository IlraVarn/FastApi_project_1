from __future__ import annotations
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator, EmailStr, ConfigDict
from datetime import datetime, UTC
from typing import Literal, ClassVar
from sqlalchemy import CheckConstraint, UniqueConstraint, Column, DateTime
from enum import Enum

#USERS
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


class UserPublic(SQLModel):
    id: int
    name: str
    email: str


#ORGANIZATIONS
class Organization(SQLModel, table=True):
    __tablename__: ClassVar[str] = "organizations"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_organization_name_non_empty"),
        )
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)


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


class MembershipPublic(SQLModel):
    id: int
    user_id: int
    organization_id: int
    status: Literal["active", "inactive"]



#ORDERS
class GateStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"    


class Gate(SQLModel, table=True):
    __tablename__: ClassVar[str] = "gates"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'submitted', 'approved', 'rejected')", 
                        name="ck_gate_status_valid"),
    )
    
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False)
    )
    organization_id: int = Field(
        nullable=False, 
        foreign_key='organizations.id',
        index=True)

    status: str = Field(default=GateStatus.DRAFT.value,
                        nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )
    #archived_at controls lyfecycle state so nullable makes it excplicit. 
    #i.e. archived_at is None => active order. Not none => archived order
    archived_at: datetime | None = Field(
        default=None, 
        sa_column=Column(
            DateTime(timezone=True),
        nullable=True)
    )
    reference: str | None = Field(default=None, nullable=True)


class OrderUpdatePatch(SQLModel):
    """ extra= forbid sends back 422 if clent sends additional field.
    rejects fields the client cannot mutate"""
    model_config = ConfigDict(extra='forbid') #type: ignore[assignment]

    total_cents: int | None = Field(default=None, ge=0)
    status: OrderStatus | None = None


class OrderUpdate(SQLModel):
    total_cents: int = Field(ge=0)
    status: OrderStatus


class GateCreateRequest(SQLModel):
    requirement_types: list[GateRequirementType]




class OrderStatusCountPublic(SQLModel):
    status: str
    count: int

    
class OrderWithItemsCreate(SQLModel):
    customer_id: int = Field(ge=1)
    status: Literal['paid', 'pending']
    items: list[ItemForOrderWithItemsCreate] = Field(min_length=1)


class OrderPublic(SQLModel):
    id: int
    created_at: datetime
    total_cents: int
    status: str

    
# class OrderDetailWithItemsPublic(SQLModel):
#     id: int
#     created_at: datetime
#     customer: CustomerPublic
#     total_cents: int
#     items: list[OrderItemPublic]
#ORDER STATE TRANSITIONS
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


class GateStateTransitionRequest(SQLModel):
    target_status: GateStatus
    reason: str | None = None

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if value == "":
            return None

        return value



#GATE REQUIREMENT (instead of OrderItem)
class GateRequirementType(str, Enum):
    COMMISSIONING_REPORT = "commissioning_report"
    AS_BUILT_DRAWINGS = "as_built_drawings"
    O_AND_M_MANUALS = "o_and_m_manuals"
    TEST_RECORDS = "test_records"

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


#GATE EVIDENCE
class GateEvidence(SQLModel, table=True):
    __tablename__: ClassVar[str] = "gate_evidence"

    __table_args__ = (
        CheckConstraint(
            "size_bytes >= 0",
            name="ck_gate_evidence_size_nonnegative",
        ),
        CheckConstraint(
            "upload_status IN ('pending', 'complete', 'failed')",
            name="ck_gate_evidence_upload_status_valid",
        ),
        CheckConstraint(
            "length(trim(original_filename)) > 0",
            name="ck_gate_evidence_filename_non_empty",
        ),
        UniqueConstraint(
            "storage_key",
            name="uq_gate_evidence_storage_key",
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

    storage_key: str = Field(nullable=False)

    original_filename: str = Field(nullable=False)

    content_type: str = Field(nullable=False)

    size_bytes: int = Field(nullable=False)

    checksum_sha256: str | None = Field(
        default=None,
        nullable=True,
    )

    upload_status: str = Field(
        default="pending",
        nullable=False,
    )

    created_by_user_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )

#ITEMS
class OrderItem(SQLModel, table=True):
    __tablename__: ClassVar[str] = "order_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_quantity_positive"),
        CheckConstraint("unit_price_cents >= 0", name="ck_order_item_unit_price_nonnegative"),
        CheckConstraint("length(trim(product_name)) > 0", name="ck_product_name_non_empty"),
    )

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(
        foreign_key="orders.id", 
        nullable=False,
        index=True)
    product_name: str = Field(nullable=False)
    quantity: int = Field(nullable=False)
    unit_price_cents: int = Field(nullable=False)


class OrderItemCreate(SQLModel):
    order_id: int = Field(ge=1)
    product_name: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    unit_price_cents: int = Field(ge=0)

    @field_validator("product_name")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value
    

class ItemForOrderWithItemsCreate(SQLModel):
    product_name: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price_cents: int = Field(ge=0)

    @field_validator("product_name")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value
    

class OrderItemPublic(SQLModel):
    id: int
    order_id: int
    product_name: str
    quantity: int
    unit_price_cents: int


#JOIN RESPONSE MODELS   
# class CustomerWithOrdersPublic(SQLModel):
#     id: int
#     name: str
#     email: str
#     orders: list[OrderSummaryPerCustomerPublic]


# class OrderSummaryPerCustomerPublic(SQLModel):
#     id: int
#     created_at: datetime
#     total_cents: int
#     status: str





#ORDERS SORT

OrderSortBy = Literal["created_at", "total_cents", "id"]
OrderSortDirection = Literal["asc", "desc"]


# ORDER_SORT_COLUMNS = {
#     "created_at": Order.created_at,
#     "total_cents": Order.total_cents,
#     "id": Order.id,
# }


#ITEMS SORT

ItemsSortDirection = Literal['asc', 'desc']
ItemSortBy = Literal[
                    "product_name", 
                    "quantity",
                    "unit_price_cents",
                    'id'
]

ITEM_SORT_COLUNMS = {
    "product_name": OrderItem.product_name,
    "quanity": OrderItem.quantity,
    "unit_price_cents": OrderItem.unit_price_cents,
    'id': OrderItem.id
}