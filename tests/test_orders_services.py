import pytest 
from errors import ConflictError, ItemNotFoundError, OrderNotFoundError, CustomerNotFoundError
from models import OrderCreate, CustomerCreate, OrderItemCreate, OrderUpdate, Order
from services.customers import (create_customer_service)
from services.orders import (create_order_service,
                             get_order_detail_service,
                             get_order_detail_with_items_service,
                             list_orders_service,
                             update_order_service,
                             delete_order_service,)
from services.items import create_item_service


def test_create_order_service_success(db_session, db_customer):

    db_order = create_order_service(
        customer_id= db_customer.id,
        total_cents=10,
        status='paid',
        session=db_session,
    )

    assert db_order.id is not None
    assert db_order.created_at is not None
    assert db_order.customer_id == db_customer.id
    assert db_order.total_cents == 10
    assert db_order.status == 'paid'


def test_create_order_service_customer_not_found(db_session):

    with pytest.raises(CustomerNotFoundError) as error:
        create_order_service(
            customer_id= 999,
            total_cents=10,
            status='paid',
            session=db_session,
    )
        
    assert error.value.detail == 'customer not found'


def test_get_order_detail_service_success(db_session, db_customer, db_order):

    returned_order, returned_customer = get_order_detail_service(
        order_id=db_order.id,
        session=db_session
    )

    assert returned_order.id == db_order.id
    assert returned_order.created_at is not None
    assert returned_order.customer_id == db_customer.id
    assert returned_order.total_cents == db_order.total_cents
    assert returned_order.status == db_order.status

    assert returned_customer.id == db_customer.id
    assert returned_customer.name == db_customer.name
    assert returned_customer.email == db_customer.email
    assert returned_customer.internal_note is None


def test_get_order_detail_service_order_not_found(db_session):

    with pytest.raises(OrderNotFoundError) as error:
        get_order_detail_service(
        order_id=999,
        session=db_session
    )
        
    assert error.value.detail == 'order not found'


def test_get_order_with_items_success(
        db_session, db_order, db_customer, db_item
        ):

    returned_order, returned_customer, returned_items = (
        get_order_detail_with_items_service(
        order_id=db_order.id,
        session=db_session)
    )
    
    assert returned_order.id == db_order.id
    assert returned_order.created_at is not None
    assert returned_order.customer_id == db_customer.id
    assert returned_order.total_cents == db_order.total_cents
    assert returned_order.status == db_order.status

    assert returned_customer.id == db_customer.id
    assert returned_customer.name == db_customer.name
    assert returned_customer.email == db_customer.email
    assert returned_customer.internal_note is None

    assert len(returned_items) == 1

    assert returned_items[0].id == db_item.id
    assert returned_items[0].order_id == db_order.id
    assert returned_items[0].product_name == db_item.product_name
    assert returned_items[0].quantity == db_item.quantity
    assert returned_items[0].unit_price_cents == db_item.unit_price_cents


def test_get_order_with_items_order_not_found(db_session):

    with pytest.raises(OrderNotFoundError) as error:
        get_order_detail_with_items_service(
        order_id=999,
        session=db_session)

    assert error.value.detail == 'order not found'


def test_get_order_detail_with_items_empty_items_list_success(
        db_session, db_customer, db_order
        ):

    returned_order, returned_customer, returned_items = (
        get_order_detail_with_items_service(
        order_id=db_order.id,
        session=db_session)
    )
    
    assert returned_order.id == db_order.id
    assert returned_order.created_at is not None
    assert returned_order.customer_id == db_order.customer_id
    assert returned_order.total_cents == db_order.total_cents
    assert returned_order.status == db_order.status

    assert returned_customer.id == db_customer.id
    assert returned_customer.name == db_customer.name
    assert returned_customer.email == db_customer.email
    assert returned_customer.internal_note is None

    assert len(returned_items) == 0


def test_list_orders_service_all_orders_success(db_session, make_db_order):

    first_order = make_db_order(total_cents = 20, status = 'paid')

    second_order = make_db_order(total_cents = 10, status = 'pending')

    returned_orders = list_orders_service(
        status=None, 
        sort_by='created_at',
        sort_dir='desc',
        offset=0, 
        limit=2,
        session=db_session)
    
    assert len(returned_orders) == 2
    assert returned_orders[0].id == second_order.id
    assert returned_orders[1].id == first_order.id


def test_list_orders_service_filters_by_status_success(db_session, make_db_order):

    first_order = make_db_order(total_cents = 20, status = 'pending')

    second_order = make_db_order(total_cents = 10, status = 'paid')
 
    returned_orders = list_orders_service(
        status='paid', 
        sort_by='created_at',
        sort_dir='desc',
        offset=0, 
        limit=2,
        session=db_session)
    
    assert len(returned_orders) == 1
    assert returned_orders[0].id == second_order.id
    assert returned_orders[0].status == second_order.status


def test_list_orders_service_paginates_success(db_session, make_db_order):

    first_order = make_db_order(total_cents = 20, status = 'paid')

    second_order = make_db_order(total_cents = 10, status = 'paid')

    returned_orders = list_orders_service(
        status='paid', 
        sort_by='created_at',
        sort_dir='desc',
        offset=1, 
        limit=1,
        session=db_session)
    
    assert len(returned_orders) == 1
    assert returned_orders[0].id == first_order.id

def test_list_orders_service_sorts_by_total_cents_success(db_session, make_db_order):

    first_order = make_db_order(total_cents = 10, status = 'paid')

    second_order = make_db_order(total_cents = 20, status = 'paid')

    third_order = make_db_order(total_cents = 30, status = 'paid')

    returned_orders = list_orders_service(
        status='paid', 
        sort_by='total_cents',
        sort_dir='desc',
        offset=0, 
        limit=20,
        session=db_session)
    
    assert len(returned_orders) == 3
    assert returned_orders[0].id == third_order.id
    assert returned_orders[1].id == second_order.id
    assert returned_orders[2].id == first_order.id


def test_list_orders_service_no_matches_returns_empty_list_success(db_session, make_db_order):

    first_order = make_db_order(total_cents = 20, status = 'paid')

    returned_orders = list_orders_service(
        status='pending', 
        sort_by='created_at',
        sort_dir='desc',
        offset=0, 
        limit=1,
        session=db_session)
    
    assert len(returned_orders) == 0
    assert returned_orders == []


def test_update_order_success(db_session, db_order):

    returned_order, returned_customer = update_order_service(
        order_id=db_order.id,
        total_cents=20,
        status='pending',
        session=db_session)
    
    assert returned_order.id == db_order.id
    assert returned_customer.id == db_order.customer_id
    assert returned_order.total_cents == 20
    assert returned_order.status == 'pending'


def test_update_order_not_found(db_session):
    
    order_update=OrderUpdate(
        total_cents=20, 
        status='pending')

    with pytest.raises(OrderNotFoundError) as error:
        update_order_service(
            order_id=999, 
            total_cents=10,
            status='paid',
            session=db_session)

    assert error.value.detail == 'order not found'


def test_delete_order_service_success(db_session, db_order):

    delete_order_service(order_id=db_order.id, session=db_session)

    assert db_session.get(Order, db_order.id) is None


def test_delete_order_service_not_found(db_session):

    with pytest.raises(OrderNotFoundError) as error:
        delete_order_service(order_id=999, session=db_session)
    
    assert error.value.detail == 'order not found'


def test_delete_order_service_with_items_raises_conflict_error(db_session, db_order, db_item):

    with pytest.raises(ConflictError) as error:
        delete_order_service(order_id=db_order.id, session=db_session)
    
    assert error.value.detail == 'order cannot be deleted with items'
    assert db_item.id is not None


