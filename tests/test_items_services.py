import pytest 
from errors import ConflictError, NotFoundError
from models import OrderItemCreate
from services.items import create_item_service, list_items_service

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



def test_list_items_service_all_items_success(db_session, make_db_item):
    
    first_item = make_db_item(product_name = 'toy', quantity = 10, unit_price_cents = 20)
    second_item = make_db_item(product_name = 'not_toy', quantity = 1, unit_price_cents = 2)

    returned_items = list_items_service(
        order_id=None,
        min_quantity=None,
        offset=0,
        limit=2,
        sort_by='product_name',
        sort_dir='asc',
        session=db_session
    )

    assert len(returned_items) == 2
    assert returned_items[0].id == second_item.id

def test_list_items_service_filters_by_min_quantity_success(db_session, make_db_item):
    
    first_item = make_db_item(product_name = 'toy', quantity = 10, unit_price_cents = 20)
    second_item = make_db_item(product_name = 'not_toy', quantity = 1, unit_price_cents = 2)

    returned_items = list_items_service(
        order_id=None,
        min_quantity=10,
        offset=0,
        limit=2,
        sort_by='product_name',
        sort_dir='asc',
        session=db_session
    )

    assert len(returned_items) == 1
    assert returned_items[0].id == first_item.id


def test_list_items_service_paginates_success(db_session, make_db_item):
    
    first_item = make_db_item(product_name = 'toy', quantity = 10, unit_price_cents = 20)
    second_item = make_db_item(product_name = 'not_toy', quantity = 1, unit_price_cents = 2)

    returned_items = list_items_service(
        order_id=None,
        min_quantity=None,
        offset=1,
        limit=1,
        sort_by='product_name',
        sort_dir='asc',
        session=db_session
    )

    assert len(returned_items) == 1
    assert returned_items[0].id == first_item.id

def test_list_items_no_matches_returns_empty_list_success(db_session, make_db_item):
    first_item = make_db_item(product_name = 'toy', quantity = 1, unit_price_cents = 20)

    returned_items = list_items_service(
        order_id=None,
        min_quantity=2,
        offset=1,
        limit=1,
        sort_by='product_name',
        sort_dir='asc',
        session=db_session
    )

    assert len(returned_items) == 0
    assert returned_items == []


#failure tests
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
                            
