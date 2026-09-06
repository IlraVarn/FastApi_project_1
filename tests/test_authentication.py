from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from auth.context import AuthContext
from auth.dependencies import get_authenticated_user
from main import app
from models import User

#container of test routes:
auth_test_router = APIRouter()


#Test-only route. Not included in the main.py
@auth_test_router.get("/auth_test/auth")
def read_me(
    current_user: AuthContext = Depends(get_authenticated_user),
) -> AuthContext:
    return current_user



#Take the route inside auth_test_router and 
# temporarily add it to main.app
#while pytest is running
#So the test route is added to the same app 
# your existing client already uses
#is inside:
# tests/test_authentication.py
# It runs only when that test module is imported.

app.include_router(auth_test_router)


#AUTHENTICATION TESTS
def test_valid_authentication(
    client,
    db_session,
    monkeypatch,
):
    db_user = User(
        name="Olga",
        email="olga@x.com",
    )

    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    assert db_user.id is not None

    monkeypatch.setenv(
        "DEV_AUTH_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "DEV_AUTH_USER_ID",
        str(db_user.id),
    )

    response = client.get(
        "/auth_test/auth",
        headers={
            "Authorization": "Bearer test-token",
        },
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == db_user.id


def test_wrong_token_is_rejected(
    client,
    db_session,
    monkeypatch,
):
    db_user = User(
        name="Olga",
        email="olga@x.com",
    )

    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    assert db_user.id is not None

    monkeypatch.setenv(
        "DEV_AUTH_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "DEV_AUTH_USER_ID",
        str(db_user.id),
    )

    response = client.get(
        "/auth_test/auth",
        headers={
            "Authorization": "Bearer wrong-token",
        },
    )

    assert response.status_code == 401


def test_missing_authorization_header_is_rejected(
    client,
):
    response = client.get(
        "/auth_test/auth",
    )

    assert response.status_code == 401


def test_nonexistent_user_is_rejected(
    client,
    monkeypatch,
):
    monkeypatch.setenv(
        "DEV_AUTH_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "DEV_AUTH_USER_ID",
        "999999",
    )

    response = client.get(
        "/auth_test/auth",
        headers={
            "Authorization": "Bearer test-token",
        },
    )

    assert response.status_code == 401


def test_archived_user_is_rejected(
    client,
    db_session,
    monkeypatch,
):
    db_user = User(
        name="Olga",
        email="olga@x.com",
        archived_at=datetime.now(UTC),
    )

    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    assert db_user.id is not None

    monkeypatch.setenv(
        "DEV_AUTH_TOKEN",
        "test-token",
    )
    monkeypatch.setenv(
        "DEV_AUTH_USER_ID",
        str(db_user.id),
    )

    response = client.get(
        "/auth_test/auth",
        headers={
            "Authorization": "Bearer test-token",
        },
    )

    assert response.status_code == 401



# normally:

# start FastAPI normally
# ↓
# main.py runs
# ↓
# test_authentication.py does NOT run
# ↓
# app.include_router(auth_test_router) does NOT happen
# ↓
# /auth_test/auth does not exist

# But pytest does load that file:

# run pytest
# ↓
# pytest loads test_authentication.py
# ↓
# creates auth_test_router
# ↓
# creates /auth_test/auth
# ↓
# app.include_router(auth_test_router)
# ↓
# main.app temporarily has the test route


# the mechanics are:

# existing client fixture
# ↓
# main.app
# ↓
# /auth_test/auth
# ↓
# Depends(get_authenticated_user)
# ↓
# HTTPBearer reads "test-token"
# ↓
# DEV_AUTH_TOKEN matches
# ↓
# DEV_AUTH_USER_ID points to db_user
# ↓
# get_session uses your conftest test DB override
# ↓
# User found and active
# ↓
# AuthContext(user_id=db_user.id)
# ↓
# route returns AuthContext
# ↓
# 200