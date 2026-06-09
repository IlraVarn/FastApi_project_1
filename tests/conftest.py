import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import models  # keeps SQLModel metadata aware of tables
from db import get_session
from main import app

from services.customers import create_customer_service
from services.orders import create_order_service
from services.items import create_item_service
from models import CustomerCreate, OrderCreate, OrderItemCreate
from typing import Literal


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session():
    with Session(test_engine) as session:
        yield session

@pytest.fixture(autouse=True)
def reset_test_database():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    app.dependency_overrides[get_session] = override_get_session

    yield

    app.dependency_overrides.clear()


#endpoint test fixtures

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def customer(client):
    response = client.post(
        "/customers",
        json={
            "name": "Olga",
            "email": "x.com",
        },
    )

    assert response.status_code == 200
    return response.json()

@pytest.fixture
def order(client, customer):
    response = client.post(
        "/orders",
        json={
            'customer_id': customer['id'],
            'total_cents': 10,
            'status': 'paid'
        },
    )

    assert response.status_code == 200
    return response.json()

@pytest.fixture
def item(client, order):
    response = client.post('/items',
         json= {
            'order_id': order['id'],
            'product_name': 'toy',
            'quantity': 10,
            'unit_price_cents': 50}
         )
    
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def make_order(client, customer):
    def _make_order(total_cents: int, status: Literal['paid', 'pending']):
        response = client.post(
            "/orders",
            json={
                "customer_id": customer["id"],
                "total_cents": total_cents,
                "status": status,
            },
        )

        assert response.status_code == 200
        return response.json()

    return _make_order


#service test fixtures
@pytest.fixture
def db_session():
    with Session(test_engine) as session:
        yield session
    

@pytest.fixture
def db_customer(db_session):
    return create_customer_service(
        customer_create=CustomerCreate(
            name="Olga",
            email="x.com",
        ),
        session=db_session,
    )


@pytest.fixture
def db_order(db_session, db_customer):
    return create_order_service(
        order_create=OrderCreate(
            customer_id=db_customer.id,
            total_cents=10,
            status="paid",
        ),
        session=db_session,
    )


@pytest.fixture
def db_item(db_session, db_order):
    return create_item_service(
        item=OrderItemCreate(
            order_id=db_order.id,
            product_name="toy",
            quantity=10,
            unit_price_cents=50,
        ),
        session=db_session,
    )

@pytest.fixture
def make_db_order(db_session, db_customer):
    def _make_db_order(
        total_cents: int,
        status: Literal['paid', 'pending'],
    ):
        return create_order_service(
            order_create=OrderCreate(
                customer_id=db_customer.id,
                total_cents=total_cents,
                status=status,
            ),
            session=db_session,
        )

    return _make_db_order

