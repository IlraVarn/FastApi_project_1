from typing import Annotated, Literal
from app.auth.dependencies import AuthContext, get_authenticated_user
from app.tenancy.context import TenantContext
from app.tenancy.dependencies import get_tenant_context
from fastapi import (APIRouter, 
                     Depends, 
                     HTTPException, 
                     Query, 
                     Response, 
                     status,
)
from sqlmodel import Session

from app.db import get_session
from app.errors import (DataIntegrityError,
                    UserNotFoundError,
                    )
from app.mappers.organization_mappers import (to_organization_public,)


from app.models import (
     OrganizationCreate,
     OrganizationPublic
     )
from app.services.organizations import create_self_service_organization_service
router = APIRouter(prefix="/organizations", tags=["organizations"])


#does not perform a tenancy check. 
#only creates org + membership if user is authorized

#checks if user exists in the DB because authenticated_user 

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

#redundant for the current architecture with get_authenticated_user()
    # except UserNotFoundError as error:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid authentication credentials",
    #     ) from error


    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization could not be created",
        ) from error

    return to_organization_public(
        db_organization
    )





