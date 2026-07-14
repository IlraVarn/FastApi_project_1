from datetime import UTC, datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col

from errors import CustomerNotFoundError, OrderNotFoundError, DataIntegrityError, ConflictError
from models import (Customer, Order, OrderCreate, OrderItem, OrderUpdate, 
                    OrderSortDirection, OrderSortBy, OrderStatus)
from typing import Literal
from sqlalchemy import asc, desc
from storage.customers import get_customer_by_id
from storage.orders import (add_order_record, 
                            get_order_by_id, 
                            update_order,
                            delete_order_record,
                            list_orders)
from storage.items import list_items_by_order_id


def create_order_service(
    customer_id: int,
    total_cents: int,
    status: str,
    session: Session,
) -> Order:
    
    db_customer = get_customer_by_id(customer_id=customer_id, 
                                     session=session)

    if db_customer is None:
        raise CustomerNotFoundError()

    db_order = add_order_record(
        customer_id=customer_id,
        total_cents=total_cents,
        status=status,
        session=session,
        )
    
    try:
        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error
    
    session.refresh(db_order)

    return db_order


def get_order_detail_service(
    order_id: int,
    session: Session,
) -> tuple[Order, Customer]:
    
    db_order = get_order_by_id(
        order_id=order_id, 
        session=session)

    if db_order is None:
        raise OrderNotFoundError()

    db_customer = get_customer_by_id(customer_id=db_order.customer_id, 
                                     session=session)

    if db_customer is None:
        raise DataIntegrityError()

    return db_order, db_customer


def get_order_detail_with_items_service(
    order_id: int,
    session: Session,
) -> tuple[Order, Customer, list[OrderItem]]:
    
    db_order, db_customer = get_order_detail_service(
        order_id=order_id,
        session=session,
    )

    db_items = list_items_by_order_id(order_id=order_id, session=session)

    return db_order, db_customer, db_items


def update_order_service(
    order_id: int,
    total_cents: int,
    status: str,
    session: Session,
) -> tuple[Order, Customer]:
    
    db_order = get_order_by_id(
        order_id=order_id, 
        session=session)

    if db_order is None:
        raise OrderNotFoundError()

    db_customer = get_customer_by_id(customer_id=db_order.customer_id, 
                                     session=session)
    
    if db_customer is None:
        raise DataIntegrityError()
    
    db_order = update_order(db_order=db_order, 
                            total_cents=total_cents, 
                            status=status, 
                            session=session)

    try:
        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    session.refresh(db_order)

    return db_order, db_customer


def delete_order_service(
    order_id: int,
    session: Session,
) -> None:
    
    db_order = get_order_by_id(
        order_id=order_id, 
        session=session)

    if db_order is None:
        raise OrderNotFoundError("order not found")
    

    db_items = list_items_by_order_id(
        order_id=order_id,
        session=session)

    if db_items:
        raise ConflictError('order cannot be deleted with items')

    delete_order_record(db_order=db_order, session=session)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error


def list_orders_service(
        *,
        session: Session,               
        status: OrderStatus | None,
        sort_by: OrderSortBy,
        sort_dir: OrderSortDirection,
        offset: int,
        limit: int,
) -> list[Order]:
    
    db_orders = list_orders(
        session=session,               
        status=status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=offset,
        limit=limit)


    return db_orders


