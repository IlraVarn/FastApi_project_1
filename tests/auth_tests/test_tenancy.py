from fastapi import APIRouter, Depends

from app.auth.context import AuthContext
from app.auth.dependencies import get_authenticated_user
from app.main import app

# Use your actual import locations for these two:
from app.tenancy.context import TenantContext
from app.tenancy.dependencies import get_tenant_context
from app.models import Organization, Membership, User

"""test_tenancy.py
    → DO NOT use authenticated_client fixture
    → explicitly supply AuthContext
    → real Membership lookup
    → test get_tenant_context()"""

# Tenancy tests are not ordinary router tests. 
# The tiny router exists only to trigger:
# get_tenant_context()
# for test_tenancy.py, use DB setup, 
# because you are directly testing the 
# Membership → TenantContext mechanism


tenancy_test_router = APIRouter()


@tenancy_test_router.get(
    "/auth_test/organizations/{organization_id}/tenant"
)
def read_tenant(
    tenant: TenantContext = Depends(get_tenant_context),
) -> TenantContext:
    return tenant


app.include_router(tenancy_test_router)


def test_active_membership_allows_tenant_access(
    client,
    db_session,
):
    db_user = User(
        name="Olga",
        email="olga@x.com",
    )

    db_organization = Organization(
        name="Acme",
    )

    db_session.add(db_user)
    db_session.add(db_organization)
    db_session.commit()

    db_session.refresh(db_user)
    db_session.refresh(db_organization)

    assert db_user.id is not None
    assert db_organization.id is not None

    user_id = db_user.id
    organization_id = db_organization.id

    db_membership = Membership(
        user_id=user_id,
        organization_id=organization_id,
        status="active",
        role="member",
    )

    db_session.add(db_membership)
    db_session.commit()

    def override_get_authenticated_user() -> AuthContext:
        return AuthContext(
            user_id=user_id,
        )

    app.dependency_overrides[get_authenticated_user] = (
        override_get_authenticated_user
    )

    response = client.get(
        f"/auth_test/organizations/{organization_id}/tenant"
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
    assert response.json()["organization_id"] == organization_id


#supply authcontext and only test tenant context

def test_missing_membership_is_rejected(
    client,
    db_session,
):
    db_user = User(
        name="Olga",
        email="olga@x.com",
    )

    db_organization = Organization(
        name="Acme",
    )

    db_session.add(db_user)
    db_session.add(db_organization)
    db_session.commit()

    db_session.refresh(db_user)
    db_session.refresh(db_organization)

    assert db_user.id is not None
    assert db_organization.id is not None

    user_id = db_user.id
    organization_id = db_organization.id

    def override_get_authenticated_user() -> AuthContext:
        return AuthContext(
            user_id=user_id,
        )

    app.dependency_overrides[get_authenticated_user] = (
        override_get_authenticated_user
    )

    response = client.get(
        f"/auth_test/organizations/{organization_id}/tenant"
    )

    assert response.status_code == 403


def test_inactive_membership_is_rejected(
    client,
    db_session,
):
    db_user = User(
        name="Olga",
        email="olga@x.com",
    )

    db_organization = Organization(
        name="Acme",
    )

    db_session.add(db_user)
    db_session.add(db_organization)
    db_session.commit()

    db_session.refresh(db_user)
    db_session.refresh(db_organization)

    assert db_user.id is not None
    assert db_organization.id is not None

    user_id = db_user.id
    organization_id = db_organization.id

    db_membership = Membership(
        user_id=user_id,
        organization_id=organization_id,
        status="inactive",
        role="member",
    )

    db_session.add(db_membership)
    db_session.commit()

    def override_get_authenticated_user() -> AuthContext:
        return AuthContext(
            user_id=user_id,
        )

    app.dependency_overrides[get_authenticated_user] = (
        override_get_authenticated_user
    )

    response = client.get(
        f"/auth_test/organizations/{organization_id}/tenant"
    )

    assert response.status_code == 403


