from datetime import UTC, datetime

from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col

from errors import ConflictError, OrderNotFoundError, DataIntegrityError
from models import (Order, OrderItemCreate, OrderItem,
                    ITEM_SORT_COLUNMS, ItemSortBy, ItemsSortDirection)
from typing import Literal
from sqlalchemy import asc, desc 
from storage.orders import get_order_by_id
from storage.items import create_item_record, list_items_sorted




def create_item_service(
    order_id: int,
    product_name: str,
    quantity: int,
    unit_price_cents: int,
    session: Session
        )->OrderItem:

    db_order = get_order_by_id(order_id=order_id, session=session)

    if db_order is None:
        raise OrderNotFoundError()
    
    db_item = create_item_record(
        order_id=order_id,
        product_name=product_name,
        quantity=quantity,
        unit_price_cents=unit_price_cents,
        session=session
    )

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError()
       
    
    session.refresh(db_item)

    return db_item


def list_items_service(*,
    order_id: int | None,
    min_quantity: int | None,
    offset: int,
    limit: int,
    sort_by: ItemSortBy,
    sort_dir: ItemsSortDirection,
    session: Session
) -> list[OrderItem] :
    
    db_items = list_items_sorted(
            order_id = order_id,
            min_quantity = min_quantity,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_dir=sort_dir,
            session=session
            )


    return db_items
