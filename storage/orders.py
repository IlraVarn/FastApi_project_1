from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from datetime import UTC, datetime
from models import (Order, OrderItem, OrderUpdate, 
                    Customer, OrderStatus, 
                    OrderSortBy, OrderSortDirection)
from models import ORDER_SORT_COLUMNS
from typing import Any


def add_order_record(
    customer_id: int,
    total_cents: int,
    status: str,
    session: Session,
    ) -> Order:
    
    db_order = Order(
        created_at=datetime.now(UTC),
        customer_id=customer_id,
        total_cents=total_cents,
        status=status,
    )

    session.add(db_order)
    return db_order


def get_order_by_id(
    *,
    order_id: int,
    session: Session,
    ) -> Order | None:
    
    return session.get(Order, order_id)


def update_order(
        *,
        db_order: Order,
        total_cents: int,
        status: str,
        session: Session,
    ) -> Order:

    db_order.total_cents = total_cents
    db_order.status = status


    session.add(db_order)
    return db_order


def delete_order_record(
        *,
        db_order: Order, 
        session: Session
        )-> None:
    
    session.delete(db_order)


def list_orders(
        *,
        session: Session,               
        status: OrderStatus | None,
        sort_by: OrderSortBy,
        sort_dir: OrderSortDirection,
        offset: int,
        limit: int
    )-> list[Order]:
    
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


def list_orders_by_customer_id(
    customer_id: int,
    session: Session,
) -> list[Order]:
    """Return all orders belonging to one customer.
    Orders are returned newest first, with ID as the stable tie-breaker.
    """

    statement = (
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(
            desc(col(Order.created_at)),
            desc(col(Order.id)),
        )
    )

    result = session.exec(statement)

    return list(result.all())


def list_order_customer_pairs(
    session: Session,
) -> list[tuple[Order, Customer]]:
    """Return every order together with its referenced customer."""

    statement = (
        select(Order, Customer)
        .join(
            Customer,
            col(Customer.id) == Order.customer_id,
        )
        .order_by(
            desc(col(Order.created_at)),
            desc(col(Order.id)),
        )
    )

    result = session.exec(statement)

    return list(result.all())


def update_order_patch(
    *,
    db_order: Order,
    update_data: dict[str, Any],
    session: Session,
) -> Order:
    """Apply validated fields to an existing Order 
    and stage it for persistence.
    Does not commit, rollback, or refresh.
    """

    db_order.sqlmodel_update(update_data)
    session.add(db_order)

    return db_order


