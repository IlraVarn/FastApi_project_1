
from sqlmodel import Session
from services.tenancy import resolve_tenant_context_service
from errors import TenantAccessDeniedError
from fastapi import Depends, HTTPException, status, Path
from auth.context import AuthContext
from tenancy.context import TenantContext
from db import get_session
from sqlmodel import Session
from auth.dependencies import get_authenticated_user


#Is this authenticated user allowed to act inside this organization?
def get_tenant_context(
    organization_id: int = Path(ge=1),
    authenticated_user: AuthContext = Depends(get_authenticated_user),
    session: Session = Depends(get_session),
) -> TenantContext:
    
    try:
        return resolve_tenant_context_service(
            actor_user_id=authenticated_user.user_id,
            organization_id=organization_id,
            session=session,
        )

    except TenantAccessDeniedError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this organization is not allowed",
        ) from error



