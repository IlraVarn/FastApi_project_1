from datetime import UTC, datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col

from errors import NotFoundError, ConflictError, CustomerNotFoundError, OrderNotFoundError, DataIntegrityError
from models import (Customer, Order, OrderCreate, OrderItem, OrderUpdate, 
                    OrderSortDirection, OrderSortBy, OrderStatus)
from typing import Literal
from sqlalchemy import asc, desc
from storage.customers import get_customer_by_id
from storage.orders import add_order_record


ORDER_SORT_COLUMNS = {
    "created_at": Order.created_at,
    "total_cents": Order.total_cents,
    "id": Order.id,
}

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
    
    db_order = session.get(Order, order_id)

    if not db_order:
        raise NotFoundError("order not found")

    db_customer = session.get(Customer, db_order.customer_id)

    if not db_customer:
        raise NotFoundError("customer not found")

    return db_order, db_customer


def get_order_detail_with_items_service(
    order_id: int,
    session: Session,
) -> tuple[Order, Customer, list[OrderItem]]:
    db_order, db_customer = get_order_detail_service(
        order_id=order_id,
        session=session,
    )

    statement = (
        select(OrderItem)
        .where(OrderItem.order_id == order_id)
        .order_by(col(OrderItem.id))
    )

    db_items = list(session.exec(statement).all())

    return db_order, db_customer, db_items


def update_order_service(
    order_id: int,
    order_update: OrderUpdate,
    session: Session,
) -> tuple[Order, Customer]:
    db_order = session.get(Order, order_id)

    if not db_order:
        raise NotFoundError("order not found")

    db_customer = session.get(Customer, db_order.customer_id)

    if not db_customer:
        raise NotFoundError("customer not found")

    db_order.total_cents = order_update.total_cents
    db_order.status = order_update.status

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    return db_order, db_customer


def delete_order_service(
    order_id: int,
    session: Session,
) -> None:
    db_order = session.get(Order, order_id)

    if not db_order:
        raise NotFoundError("order not found")
    
    statement= (select(OrderItem)
                .where(OrderItem.order_id == order_id)
    )
    db_items = list(session.exec(statement).all())
    if db_items:
        raise ConflictError('order cannot be deleted with items')


    session.delete(db_order)
    session.commit()

def list_orders_service(
        *,
        session: Session,               
        status: OrderStatus | None,
        sort_by: OrderSortBy,
        sort_dir: OrderSortDirection,
        offset: int,
        limit: int,
) -> list[Order]:
    
    statement = select(Order)

    if status is not None:
        statement = statement.where(Order.status == status)

    sort_column = ORDER_SORT_COLUMNS[sort_by]

    if sort_dir == "desc":
        primary_sort = desc(sort_column)
        tie_breaker = desc(col(Order.id))
    else:
        primary_sort = asc(sort_column)
        tie_breaker = asc(col(Order.id))

    if sort_by == "id":
        statement = statement.order_by(primary_sort)
    else:
        statement = statement.order_by(primary_sort, tie_breaker)

    statement = statement.offset(offset).limit(limit)

    db_orders = list(session.exec(statement).all())

    return db_orders

