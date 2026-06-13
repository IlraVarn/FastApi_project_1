import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, UTC

from models import Customer, Order, OrderItem

def test_customer_email_unique_constraint(db_session):
    first_customer = Customer(
        name="Olga",
        email="x.com",
    )

    second_customer = Customer(
        name="Ana",
        email="x.com",
    )

    db_session.add(first_customer)
    db_session.commit()

    db_session.add(second_customer)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_order_customer_id_foreign_key_constraint(db_session):
    db_order = Order(
        customer_id=999,
        created_at=datetime.now(UTC),
        total_cents=10,
        status="paid",
    )

    db_session.add(db_order)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_order_item_order_id_foreign_key_constraint(db_session):
    db_item = OrderItem(
        order_id=999,
        product_name="toy",
        quantity=1,
        unit_price_cents=50,
    )

    db_session.add(db_item)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

