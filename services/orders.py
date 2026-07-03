from datetime import UTC, datetime

from sqlmodel import Session, select, col

from errors import NotFoundError, ConflictError
from models import Customer, Order, OrderCreate, OrderItem, OrderUpdate
from typing import Literal
from sqlalchemy import asc, desc


OrderSortBy = Literal["created_at", "total_cents", "id"]
SortDirection = Literal["asc", "desc"]

OrderStatus = Literal["paid", "pending"]

ORDER_SORT_COLUMNS = {
    "created_at": Order.created_at,
    "total_cents": Order.total_cents,
    "id": Order.id,
}

def create_order_service(
    order_create: OrderCreate,
    session: Session,
) -> Order:
    
    db_customer = session.get(Customer, order_create.customer_id)

    if not db_customer:
        raise NotFoundError("customer not found")

    db_order = Order(
        created_at=datetime.now(UTC),
        customer_id=order_create.customer_id,
        total_cents=order_create.total_cents,
        status=order_create.status,
    )

    session.add(db_order)
    session.commit()
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
        sort_dir: SortDirection,
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

