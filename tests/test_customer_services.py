import pytest 
from errors import ConflictError, NotFoundError
from models import CustomerCreate
from services.customers import (create_customer_service,
                                read_customer_service)



def test_create_customer_service_success(db_session):
    customer_create = CustomerCreate(
        name="Olga",
        email="x.com",
    )

    db_customer = create_customer_service(
        customer_create=customer_create,
        session=db_session,
    )

    assert db_customer.id is not None
    assert db_customer.name == customer_create.name
    assert db_customer.email == customer_create.email
    assert db_customer.internal_note is None


def test_create_customer_service_duplicate_email(db_session, db_customer):

    duplicate_customer = CustomerCreate(
        name="Olga 2",
        email=db_customer.email
    )

    with pytest.raises(ConflictError) as captured_error:
        create_customer_service(
            customer_create=duplicate_customer,
            session=db_session,
        )

    assert captured_error.value.detail == "customer email already exists"


def test_read_customer_service_success(db_session, db_customer):

    customer_id = db_customer.id

    returned_customer = read_customer_service(customer_id, db_session)

    assert returned_customer.id == customer_id
    assert returned_customer.name == db_customer.name
    assert returned_customer.email == db_customer.email
    assert returned_customer.internal_note is None


def test_read_customer_service_customer_not_found(db_session):
    with pytest.raises(NotFoundError) as captured_error:
        read_customer_service(
            customer_id=999,
            session=db_session,
        )

    assert captured_error.value.detail == "customer not found"