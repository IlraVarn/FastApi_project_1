from datetime import UTC, datetime

from sqlalchemy import desc, asc
from sqlmodel import Session, select, col

from errors import NotFoundError, ConflictError
from models import (Customer, CustomerCreate,
                    Order, OrderCreate, 
                    OrderItem, OrderUpdate)
from typing import Literal

CustomerSortBy = Literal["id", "name", "email"]
SortDirection = Literal["asc", "desc"]

CUSTOMER_SORT_COLUMNS = {
        'name': col(Customer.name),
        'email': col(Customer.email),
        'id': col(Customer.id)
    }

def create_customer_service(
        customer_create: CustomerCreate, 
        session: Session
    ) -> Customer:
    
    statement = (select(Customer)
                 .where(Customer.email == customer_create.email))
    
    existing_customer = session.exec(statement).first()

    if existing_customer:
        raise ConflictError("customer email already exists")

    db_customer = Customer(
        name= customer_create.name,
        email= customer_create.email, 
        internal_note= None
    )
    session.add(db_customer)
    session.commit()
    session.refresh(db_customer)

    return db_customer


def read_customer_service(
    customer_id: int,
    session: Session ,
) -> Customer:
    
    db_customer = session.get(Customer, customer_id)
    if not db_customer:
        raise NotFoundError('customer not found')
    return db_customer


def list_customers_service(*,
    name: str | None,
    email: str | None,
    sort_by: CustomerSortBy,
    sort_dir: SortDirection ,
    offset: int,
    limit: int,
    session: Session
    ) -> list[Customer]:
    

    statement = select(Customer)

    if name is not None:
        statement = statement.where(Customer.name == name)

    if email is not None:
        statement = statement.where(Customer.email == email)

    sort_column = CUSTOMER_SORT_COLUMNS[sort_by]
    

    if sort_dir == 'desc':
        primary_sort = desc(sort_column)
        tie_breaker = desc(col(Customer.id))
    else:
        primary_sort = asc(sort_column)
        tie_breaker = asc(col(Customer.id))

    if sort_by == 'id':
        statement = statement.order_by(primary_sort)
    else:
        statement = statement.order_by(primary_sort, tie_breaker)
    

    statement = statement.offset(offset).limit(limit)

    db_customers = list(session.exec(statement).all())

    return db_customers