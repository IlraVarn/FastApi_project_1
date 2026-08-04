from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from models import (OrderItem, 
                    ITEM_SORT_COLUNMS, 
                    ItemSortBy, 
                    ItemsSortDirection)



def create_item_record(
        *,
        order_id: int,
        product_name: str,
        quantity: int,
        unit_price_cents: int,
        session: Session):


    db_item = OrderItem(
        order_id=order_id,
        product_name=product_name,
        quantity=quantity,
        unit_price_cents=unit_price_cents
    )
    session.add(db_item)

    return db_item


def list_items_by_order_id(
        *,
        order_id: int,
        session: Session
    )-> list[OrderItem]:
    

    statement = (
        select(OrderItem)
        .where(OrderItem.order_id == order_id)
        .order_by(col(OrderItem.id))
    )
    db_items = list(session.exec(statement).all())

    return db_items


def list_items_sorted(*,
    order_id: int | None,
    min_quantity: int | None,
    offset: int,
    limit: int,
    sort_by: ItemSortBy,
    sort_dir: ItemsSortDirection,
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


