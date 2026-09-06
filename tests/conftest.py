import pytest
import os

from auth.context import AuthContext
from auth.dependencies import get_authenticated_user
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from datetime import UTC, datetime

import models  # keeps SQLModel metadata aware of tables
from db import get_session
from main import app

# from services.customers import create_customer_service
# from services.gates import create_order_service
# from services.requirements import create_item_service
from models import (
    User,
    Membership,
    Organization,
    Gate,
    GateType,
    GateRequirement,
    GateEvidence,
    )

from typing import Literal

os.environ["DEV_AUTH_TOKEN"] = "test-token"

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://ilravarn@localhost:5432/fastapi_learning_test",
)

if not TEST_DATABASE_URL.endswith("/fastapi_learning_test"):
    raise RuntimeError(
        "Tests must run against fastapi_learning_test"
    )

test_engine = create_engine(TEST_DATABASE_URL)

def override_get_session():
    with Session(test_engine) as session:
        yield session

@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer test-token"
    } 

@pytest.fixture(autouse=True)
def reset_test_database():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    #added line
    app.dependency_overrides.clear()

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




#USERS
@pytest.fixture
def user(client):
    response = client.post(
        "/users",
        json={
            "name": "Olga",
            "email": "olga@x.com",
        },
    )

    assert response.status_code == 201
    return response.json()



@pytest.fixture
def authenticated_client(client, user):
    def override_get_current_user() -> AuthContext:
        return AuthContext(
            user_id=user["id"],
        )

    app.dependency_overrides[get_authenticated_user] = (
        override_get_current_user
    )

    yield client

    app.dependency_overrides.pop(
        get_authenticated_user,
        None,
    )


@pytest.fixture
def make_user(client):
    def _make_user(name: str, email: str):
        response = client.post(
            '/users',
            json={
                "name": name,
                "email": email,
            },
        )
        assert response.status_code == 201
        return response.json()
    
    return _make_user

#ORGANIZATIONS
@pytest.fixture
def organization(client, auth_headers):
    response = client.post(
        "/organizations",
        json={
            'name': 'test_organization',
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    return response.json()

@pytest.fixture
def make_organization(client, auth_headers):
    def _make_organization(name: str):
        response = client.post(
            "/organizations",
            json={
                'name': name,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        return response.json()

    return _make_organization





"""conftest client
        ↓
     main.app
        ├── test DB override
        │
        └── auth_test_router
                ↓
          /auth_test/auth
                ↓
       get_authenticated_user()"""




# #ITEMS
# @pytest.fixture
# def item(client, order):
#     response = client.post('/items',
#          json= {
#             'order_id': order['id'],
#             'product_name': 'toy',
#             'quantity': 10,
#             'unit_price_cents': 50}
#          )
    
#     assert response.status_code == 201
#     return response.json()

# @pytest.fixture
# def make_item(client, order):
#     def _make_item(product_name: str, quantity: int, unit_price_cents: int):
#         response = client.post(
#             "/items",
#             json={
#                 "order_id": order["id"],
#                 "product_name": product_name,
#                 "quantity": quantity,
#                 "unit_price_cents": unit_price_cents,
#             },
#         )

#         assert response.status_code == 201
#         return response.json()

#     return _make_item



# #SERVICE TEST FIXTURES


# @pytest.fixture
# def db_customer(db_session):
#     return create_customer_service(
#             name="Olga",
#             email="olga@x.com",
#             session=db_session,
#     )

# @pytest.fixture
# def make_db_customer(db_session):
#     def _make_db_customer(name: str, email: str):
        
#         return create_customer_service(
#             name=name,
#             email=email,
#             session=db_session
#         )
    
#     return _make_db_customer

# @pytest.fixture
# def db_user(db_session):
#     user = User(
#         email="test@example.com"
#     )
#     db_session.add(user)
#     db_session.commit()
#     db_session.refresh(user)
#     return user

# @pytest.fixture
# def db_order(db_session, db_customer, db_user):
#     return create_order_service(
#             customer_id=db_customer.id,
#             owner_id=db_user.id,
#             total_cents=10,
#             status="paid",
#             session=db_session,
#     )

# @pytest.fixture
# def make_db_order(db_session, db_customer, db_user):
#     def _make_db_order(
#         total_cents: int,
#         status: Literal['paid', 'pending'],
#     ):
#         return create_order_service(
#                 customer_id=db_customer.id,
#                 owner_id=db_user.id,
#                 total_cents=total_cents,
#                 status=status,
#                 session=db_session,
#         )

#     return _make_db_order


# @pytest.fixture
# def make_db_order_for_query(db_session, db_customer, db_user):
#     def _make_db_order(
#         total_cents: int,
#         status: Literal['paid', 'pending'],
#         archived_at: datetime | None = None,
#     ):
#         db_order= Order(
#             created_at=datetime.now(UTC),
#             customer_id=db_customer.id,
#             owner_id=db_user.id,
#             total_cents=total_cents,
#             status=status,
#             archived_at=archived_at
#         )

#         db_session.add(db_order)
#         db_session.commit()
#         db_session.refresh(db_order)

#         return db_order

#     return _make_db_order



# @pytest.fixture
# def db_item(db_session, db_order):
#     return create_item_service(
#             order_id=db_order.id,
#             product_name="toy",
#             quantity=10,
#             unit_price_cents=50,
#         session=db_session,
#     )

# @pytest.fixture
# def make_db_item(db_session, db_order):
#     def _make_db_item(
#             product_name:str,
#             quantity: int,
#             unit_price_cents: int
#     ):
#         return create_item_service(
#                 order_id=db_order.id,
#                 product_name=product_name,
#                 quantity=quantity,
#                 unit_price_cents=unit_price_cents,
#                 session=db_session
#         )

#     return _make_db_item


# @pytest.fixture
# def make_db_item_for_order(db_session, db_order):
#     def _make_db_item(
#             *,
#             order_id: int,
#             product_name:str,
#             quantity: int,
#             unit_price_cents: int
#     ):
#         return create_item_service(
#                 order_id=order_id,
#                 product_name=product_name,
#                 quantity=quantity,
#                 unit_price_cents=unit_price_cents,
#                 session=db_session
#         )

#     return _make_db_item


# @pytest.fixture
# def make_item_input():
#     def _make_item_input(
#             product_name:str,
#             quantity: int,
#             unit_price_cents: int
#     ) -> ItemForOrderWithItemsCreate:
#         return ItemForOrderWithItemsCreate(
#                 product_name=product_name,
#                 quantity=quantity,
#                 unit_price_cents=unit_price_cents,
#         )

#     return _make_item_input



