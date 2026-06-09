from datetime import UTC, datetime

from sqlalchemy import desc
from sqlmodel import Session, select, col

from errors import NotFoundError, ConflictError
from models import (Order, OrderItemCreate, OrderItem,)




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

