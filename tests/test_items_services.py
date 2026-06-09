import pytest 
from errors import ConflictError, NotFoundError
from models import OrderItemCreate
from services.items import create_item_service

def test_create_item_success(db_session, db_order):

    item_create = OrderItemCreate(
            order_id=db_order.id,
            product_name='toy',
            quantity=10,
            unit_price_cents=50)

    db_item = create_item_service(
        item=item_create,
        session=db_session)
    

    assert db_item.id is not None
    assert db_item.order_id == db_order.id
    assert db_item.product_name == item_create.product_name
    assert db_item.quantity == item_create.quantity
    assert db_item.unit_price_cents == item_create.unit_price_cents



def test_create_item_order_not_found(db_session):

    with pytest.raises(NotFoundError) as error:
        create_item_service(
            item=OrderItemCreate(
                order_id=999,
                product_name='toy',
                quantity=10,
                unit_price_cents=50),
            session=db_session)
        
    assert error.value.detail == 'order not found'
                            