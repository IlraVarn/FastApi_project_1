from datetime import UTC, datetime

from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col

from errors import (DuplicateCustomerEmailError, 
                    CustomerNotFoundError, 
                    DataIntegrityError)

from models import (Customer, CustomerCreate,
                    Order, OrderCreate, 
                    OrderItem, OrderUpdate,
                    CustomerSortBy,
                    CustomerSortDirection)
from storage.customers import (get_customer_by_email, 
                               get_customer_by_id,
                               add_customer_record,
                               list_customer_records)

from storage.orders import list_orders_by_customer_id
from typing import Literal



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
        raise CustomerNotFoundError()
    
    return db_customer


def list_customers_service(
    *,
    name: str | None,
    email: str | None,
    sort_by: CustomerSortBy,
    sort_dir: CustomerSortDirection ,
    offset: int,
    limit: int,
    session: Session
    ) -> list[Customer]:
    
    db_customers = list_customer_records(
        name=name,
        email=email,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=offset,
        limit=limit,
        session=session
    )

    return db_customers


def get_customer_with_orders_service(
    customer_id: int,
    session: Session,
) -> tuple[Customer, list[Order]]:
    """Return one customer and all orders belonging to that customer.

    Raises:
        CustomerNotFoundError:
            If the requested customer does not exist.
    """

    db_customer = get_customer_by_id(
        customer_id=customer_id,
        session=session,
    )

    if db_customer is None:
        raise CustomerNotFoundError()

    db_orders = list_orders_by_customer_id(
        customer_id=customer_id,
        session=session,
    )

    return db_customer, db_orders