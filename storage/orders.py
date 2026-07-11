from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from models import Customer
from datetime import UTC, datetime
from models import Order


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
