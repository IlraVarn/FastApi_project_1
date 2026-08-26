from storage.gates import list_order_customer_pairs
from models import Customer, Order
from datetime import UTC, datetime

from services.gates import create_order_service
from storage.gates import list_order_customer_pairs


#JOIN test
def test_list_order_customer_pairs_returns_matching_pairs(
    db_session,
    make_db_customer,
):
    first_customer = make_db_customer(
        name="First Customer",
        email="first@example.com",
    )

    second_customer = make_db_customer(
        name="Second Customer",
        email="second@example.com",
    )

    assert first_customer.id is not None
    assert second_customer.id is not None

    def make_order_for_customer(
        *,
        customer_id: int,
        total_cents: int,
        status: str,
    ):
        return create_order_service(
            customer_id=customer_id,
            total_cents=total_cents,
            status=status,
            session=db_session,
        )

    first_order = make_order_for_customer(
        customer_id=first_customer.id,
        total_cents=1000,
        status="pending",
    )

    second_order = make_order_for_customer(
        customer_id=second_customer.id,
        total_cents=2000,
        status="pending",
    )

    assert first_order.id is not None
    assert second_order.id is not None

    pairs = list_order_customer_pairs(
        session=db_session,
    )

    order_customer_id_pairs= []
    
    for db_order, db_customer in pairs:
        order_customer_id_pair = (db_order.id, db_customer.id)
        order_customer_id_pairs.append(order_customer_id_pair)
    
  

    assert (
        first_order.id,
        first_customer.id,
    ) in order_customer_id_pairs

    assert (
        second_order.id,
        second_customer.id,
    ) in order_customer_id_pairs