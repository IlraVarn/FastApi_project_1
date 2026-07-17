from sqlmodel import Field, SQLModel
from pydantic import field_validator, EmailStr
from datetime import datetime, UTC
from typing import Literal
from sqlalchemy import CheckConstraint


#CUSTOMERS
class Customer(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_customer_name_non_empty"),
        CheckConstraint("length(trim(email)) > 0", name="ck_customer_email_non_empty"),
        )
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, index=True, unique=True)
    internal_note: str | None = None

    
class CustomerCreate(SQLModel):
    name: str = Field(min_length=1)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value
    
    @field_validator("email")
    @classmethod
    def strip_lower(cls, value: str) -> str:
        value = value.strip().lower()

        return value


class CustomerPublic(SQLModel):
    id: int
    name: str
    email: str


#ORDERS
class Order(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("customer_id > 0", name="ck_customer_id_positive"),
        CheckConstraint("total_cents > 0", name="ck_total_cents_non_negative"),
        CheckConstraint("status IN ('paid', 'pending')", name="ck_order_status_valid"),
        )
    
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(nullable=False)
    customer_id: int = Field(nullable=False, foreign_key='customer.id')
    total_cents: int = Field(nullable=False)
    status: str = Field(nullable=False)


class OrderCreate(SQLModel):
    customer_id: int = Field(ge=1)
    total_cents: int = Field(ge=0)
    status: Literal['paid', 'pending']

    @field_validator("status", mode='before')
    @classmethod
    def normalize_status(cls, value):
        if isinstance(value, str):
            return value.strip().lower()

        return value
    
    
class OrderWithItemsCreate(SQLModel):
    customer_id: int = Field(ge=1)
    status: Literal['paid', 'pending']
    items: list[ItemForOrderWithItemsCreate] = Field(min_length=1)


class OrderUpdate(SQLModel):
    total_cents: int = Field(ge=0)
    status: Literal['paid', 'pending']


class OrderPublic(SQLModel):
    id: int
    created_at: datetime
    customer_id: int
    total_cents: int
    

class OrderDetailPublic(SQLModel):
    id: int
    created_at: datetime
    customer: CustomerPublic
    total_cents: int
  
    
class OrderDetailWithItemsPublic(SQLModel):
    id: int
    created_at: datetime
    customer: CustomerPublic
    total_cents: int
    items: list[OrderItemPublic]


#ITEMS
class OrderItem(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_quantity_positive"),
        CheckConstraint("unit_price_cents >= 0", name="ck_order_item_unit_price_nonnegative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", nullable=False)
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


#CUSTOMERS SORT

CustomerSortBy = Literal["id", "name", "email"]
CustomerSortDirection = Literal["asc", "desc"]


#ORDERS SORT

OrderSortBy = Literal["created_at", "total_cents", "id"]
OrderSortDirection = Literal["asc", "desc"]
OrderStatus = Literal["paid", "pending"]

ORDER_SORT_COLUMNS = {
    "created_at": Order.created_at,
    "total_cents": Order.total_cents,
    "id": Order.id,
}


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