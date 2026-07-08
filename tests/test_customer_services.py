import pytest 
from errors import DuplicateCustomerEmailError, CustomerNotFoundError
from models import CustomerCreate
from services.customers import (create_customer_service,
                                read_customer_service,
                                list_customers_service,)


#SUCCESS TESTS

def test_create_customer_service_success(db_session):

    db_customer = create_customer_service(
        name="Olga",
        email="x.com",
        session=db_session,
    )

    assert db_customer.id is not None
    assert db_customer.name == 'Olga'
    assert db_customer.email == 'x.com'
    assert db_customer.internal_note is None

def test_read_customer_service_success(db_session, db_customer):

    customer_id = db_customer.id

    returned_customer = read_customer_service(customer_id, db_session)

    assert returned_customer.id == customer_id
    assert returned_customer.name == db_customer.name
    assert returned_customer.email == db_customer.email
    assert returned_customer.internal_note is None

def test_list_customers_service_all_customers_success(db_session, make_db_customer):
    
    first_customer = make_db_customer(name = 'Ana', email= 'ana@x.com')
    second_customer = make_db_customer(name = 'Olga', email= 'olga@x.com')

    returned_customers = list_customers_service(
         name=None,
         email=None,
         sort_by='name',
         sort_dir='asc',
         offset=0,
         limit=2,
         session=db_session
    )

    assert len(returned_customers) == 2
    assert returned_customers[0].id == first_customer.id

def test_list_customers_filter_by_name_success(db_session, make_db_customer):
    
    first_customer = make_db_customer(name = 'Ana', email= 'ana@x.com')
    second_customer = make_db_customer(name = 'Olga', email= 'olga@x.com')

    returned_customers = list_customers_service(
         name='Ana',
         email=None,
         sort_by='name',
         sort_dir='asc',
         offset=0,
         limit=2,
         session=db_session
    )

    assert len(returned_customers) == 1
    assert returned_customers[0].id == first_customer.id
    assert returned_customers[0].name == first_customer.name

def test_list_customers_filter_by_email_success(db_session, make_db_customer):
    
    first_customer = make_db_customer(name = 'Ana', email= 'ana@x.com')
    second_customer = make_db_customer(name = 'Olga', email= 'olga@x.com')

    returned_customers = list_customers_service(
         name=None,
         email='olga@x.com',
         sort_by='name',
         sort_dir='asc',
         offset=0,
         limit=2,
         session=db_session
    )

    assert len(returned_customers) == 1
    assert returned_customers[0].id == second_customer.id
    assert returned_customers[0].email == second_customer.email


def test_list_customers_paginates_success(db_session, make_db_customer):

    first_customer = make_db_customer(name = 'Ana', email= 'ana@x.com')
    second_customer = make_db_customer(name = 'Olga', email= 'olga@x.com')
    third_customer = make_db_customer(name = 'Bob', email= 'bob@x.com')


    returned_customers = list_customers_service(
         name=None,
         email=None,
         sort_by='name',
         sort_dir='desc',
         offset=1,
         limit=1,
         session=db_session
    )

    assert len(returned_customers) == 1
    assert returned_customers[0].id == third_customer.id
    assert returned_customers[0].name == third_customer.name

def test_list_customers_no_matches_returns_empty_list_success(db_session, make_db_customer):
        
    first_customer = make_db_customer(name = 'Ana', email= 'ana@x.com')

    returned_customers = list_customers_service(
         name='Olga',
         email=None,
         sort_by='name',
         sort_dir='desc',
         offset=1,
         limit=1,
         session=db_session
    )

    assert len(returned_customers) == 0
    assert returned_customers == []

#FAILURE TESTS
def test_create_customer_service_duplicate_email(db_session, db_customer):


    with pytest.raises(DuplicateCustomerEmailError) as captured_error:
        create_customer_service(
            name='Olga',
            email=db_customer.email,
            session=db_session,
        )

    assert captured_error.value.detail == "customer email already exists"

def test_read_customer_service_customer_not_found(db_session):
    with pytest.raises(CustomerNotFoundError) as captured_error:
        read_customer_service(
            customer_id=999,
            session=db_session,
        )

    assert captured_error.value.detail == "customer not found"