from sqlmodel import Field, SQLModel
from pydantic import field_validator
from datetime import datetime, UTC
from typing import Literal


#customers
class Customer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    internal_note: str | None = None

class CustomerCreate(SQLModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def strip_and_reject_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value
    
    @field_validator("email")
    @classmethod
    def strip_lower_and_reject_blank(cls, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise ValueError("must not be blank")

        return value

#Response models: Customers
class CustomerPublic(SQLModel):
    id: int
    name: str
    email: str

#orders
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    customer_id: int 
    total_cents: int 
    status: str 
    
    
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


class OrderUpdate(SQLModel):
    total_cents: int = Field(ge=0)
    status: Literal['paid', 'pending']

#Response models: Orders

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

#items
class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int
    product_name: str
    quantity: int
    unit_price_cents: int

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

#Response models: Items
class OrderItemPublic(SQLModel):
    id: int
    order_id: int
    product_name: str
    quantity: int
    unit_price_cents: int








