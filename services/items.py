from datetime import UTC, datetime

from sqlalchemy import desc
from sqlmodel import Session, select, col

from errors import NotFoundError, ConflictError
from models import (Order, OrderItemCreate, OrderItem,)
from typing import Literal
from sqlalchemy import asc, desc 

SortDirection = Literal['asc', 'desc']
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


def create_item_service(
        item: OrderItemCreate, 
        session: Session
        )->OrderItem:

    order = session.get(Order, item.order_id)

    if not order:
        raise NotFoundError('order not found')
    
    db_item = OrderItem(
        order_id=item.order_id,
        product_name=item.product_name,
        quantity=item.quantity,
        unit_price_cents=item.unit_price_cents
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)

    return db_item


def list_items_service(*,
    order_id: int | None,
    min_quantity: int | None,
    offset: int,
    limit: int,
    sort_by: ItemSortBy,
    sort_dir: SortDirection,
    session: Session
) -> list[OrderItem] :
    
    statement = select(OrderItem)

    if order_id is not None:
        statement = statement.where(
            OrderItem.order_id == order_id)

    if min_quantity is not None:
        statement = statement.where(
            OrderItem.quantity >= min_quantity)

    sort_column = ITEM_SORT_COLUNMS[sort_by]

    if sort_dir == 'asc':
        primary_sort = asc(sort_column)
        tie_breaker = asc(col(OrderItem.id))
    else:
        primary_sort = desc(sort_column)
        tie_breaker = desc(col(OrderItem.id))

    if sort_by == 'id':
        statement = statement.order_by(primary_sort)
    else:
        statement = statement.order_by(primary_sort, tie_breaker)
    

    statement = statement.offset(offset).limit(limit)

    db_items = list(session.exec(statement).all())

    return db_items