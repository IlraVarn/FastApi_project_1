from datetime import UTC, datetime

from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col

from errors import (DuplicateCustomerEmailError, 
                    CustomerNotFoundError, 
                    DataIntegrityError)

from models import (Customer, CustomerCreate,
                    Order, OrderCreate, 
                    OrderItem, OrderUpdate)
from storage.customers import (get_customer_by_email, 
                               get_customer_by_id,
                               add_customer_record)
from typing import Literal

CustomerSortBy = Literal["id", "name", "email"]
SortDirection = Literal["asc", "desc"]

CUSTOMER_SORT_COLUMNS = {
        'name': col(Customer.name),
        'email': col(Customer.email),
        'id': col(Customer.id)
    }



def create_customer_service(
    *,
    name: str,
    email: str,
    session: Session,
) -> Customer:
    
    existing_customer = get_customer_by_email(
        email=email,
        session=session,
    )

    if existing_customer is not None:
        raise DuplicateCustomerEmailError()

    db_customer = add_customer_record(
        name=name,
        email=email,
        session=session,
    )

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    session.refresh(db_customer)

    return db_customer



def read_customer_service(
    customer_id: int,
    session: Session ,
) -> Customer:
    
    db_customer = get_customer_by_id(
        customer_id=customer_id,
        session=session)
    
    if db_customer is None:
        raise CustomerNotFoundError('customer not found')
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