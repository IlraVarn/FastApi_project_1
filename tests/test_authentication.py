from datetime import UTC, datetime

from models import User


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
        "/dev_onboarding/me",
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
        "/dev_onboarding/me",
        headers={
            "Authorization": "Bearer wrong-token",
        },
    )

    assert response.status_code == 401


def test_missing_authorization_header_is_rejected(
    client,
):
    response = client.get(
        "/dev_onboarding/me",
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
        "/dev_onboarding/me",
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
        "/dev_onboarding/me",
        headers={
            "Authorization": "Bearer test-token",
        },
    )

    assert response.status_code == 401