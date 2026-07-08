import pytest
import os
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

from sqlalchemy import event


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite://",
)


if TEST_DATABASE_URL.startswith("sqlite"):
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    assert "test" in TEST_DATABASE_URL

    test_engine = create_engine(
        TEST_DATABASE_URL,
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


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    with Session(test_engine) as session:
        yield session

#endpoint test fixtures

#CUSTOMERS
@pytest.fixture
def customer(client):
    response = client.post(
        "/customers",
        json={
            "name": "Olga",
            "email": "x.com",
        },
    )

    assert response.status_code == 201
    return response.json()


@pytest.fixture
def make_customer(client):
    def _make_customer(name: str, email: str):
        response = client.post(
            '/customers',
            json={
                "name": name,
                "email": email,
            }
        )
        assert response.status_code == 201
        return response.json()
    
    return _make_customer

#ORDERS
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


#ITEMS
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
def make_item(client, order):
    def _make_item(product_name: str, quantity: int, unit_price_cents: int):
        response = client.post(
            "/items",
            json={
                "order_id": order["id"],
                "product_name": product_name,
                "quantity": quantity,
                "unit_price_cents": unit_price_cents,
            },
        )

        assert response.status_code == 200
        return response.json()

    return _make_item



#service test fixtures


@pytest.fixture
def db_customer(db_session):
    return create_customer_service(
            name="Olga",
            email="x.com",
            session=db_session,
    )

@pytest.fixture
def make_db_customer(db_session):
    def _make_db_customer(name: str, email: str):
        
        return create_customer_service(
            name=name,
            email=email,
            session=db_session
        )
    
    return _make_db_customer

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
def make_db_item(db_session, db_order):
    def _make_db_item(
            product_name:str,
            quantity: int,
            unit_price_cents: int
    ):
        return create_item_service(
            item=OrderItemCreate(
                order_id=db_order.id,
                product_name=product_name,
                quantity=quantity,
                unit_price_cents=unit_price_cents
            ),
            session=db_session
        )

    return _make_db_item


@pytest.fixture
def make_db_item_for_order(db_session, db_order):
    def _make_db_item(
            *,
            order_id: int,
            product_name:str,
            quantity: int,
            unit_price_cents: int
    ):
        return create_item_service(
            item=OrderItemCreate(
                order_id=order_id,
                product_name=product_name,
                quantity=quantity,
                unit_price_cents=unit_price_cents
            ),
            session=db_session
        )

    return _make_db_item