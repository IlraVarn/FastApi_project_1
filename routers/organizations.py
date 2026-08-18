from typing import Annotated, Literal
from auth.dependencies import AuthContext, get_authenticated_user
from tenancy.context import TenantContext
from tenancy.dependencies import get_tenant_context
from fastapi import (APIRouter, 
                     Depends, 
                     HTTPException, 
                     Query, 
                     Response, 
                     status,
)
from sqlmodel import Session

from db import get_session
from errors import (DataIntegrityError,
                    UserNotFoundError)
from mappers import (to_organization_public,)


from models import (
     OrganizationCreate,
     OrganizationPublic
     )
from services.organizations import create_self_service_organization_service
router = APIRouter(prefix="/organizations", tags=["organizations"])






@router.post(
    "",
    response_model=OrganizationPublic,
    status_code=status.HTTP_201_CREATED,
)

def create_organization(
    organization: OrganizationCreate,
    authenticated_user: AuthContext = Depends(get_authenticated_user),
    session: Session = Depends(get_session),
):
    try:
        db_organization = create_self_service_organization_service(
            organization_name=organization.name,
            actor_user_id=authenticated_user.user_id,
            session=session,
        )

    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization could not be created",
        ) from error

    return to_organization_public(
        db_organization
    )





