from datetime import UTC, datetime

from sqlalchemy import desc
from sqlmodel import Session, select, col

from errors import NotFoundError, ConflictError
from models import Customer, Order, OrderCreate, OrderItem, OrderUpdate

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


def list_orders_service(
     status: str|None,
        offset: int,
        limit: int,
        session: Session
) -> list[Order]:
    statement = select(Order)

    if status is not None:
        statement = statement.where(Order.status == status)

    statement = (
        statement
        .order_by(desc(col(Order.created_at)), desc(col(Order.id)))
        .offset(offset)
        .limit(limit)
    )

    db_orders = list(session.exec(statement).all())

    return db_orders


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
