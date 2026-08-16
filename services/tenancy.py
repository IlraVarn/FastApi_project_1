from sqlmodel import Session

from auth.context import TenantContext
from errors import TenantAccessDeniedError
from storage.memberships import get_active_membership_record


def resolve_tenant_context_service(
    *,
    actor_user_id: int,
    organization_id: int,
    session: Session,
) -> TenantContext:
    
    membership = get_active_membership_record(
        user_id=actor_user_id,
        organization_id=organization_id,
        session=session,
    )

    if membership is None:
        raise TenantAccessDeniedError()

    return TenantContext(
        user_id=actor_user_id,
        organization_id=organization_id,
    )


