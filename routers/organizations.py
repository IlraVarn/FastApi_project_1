from typing import Annotated, Literal
from auth.dependencies import AuthContext, get_current_user
from auth.context import TenantContext
from auth.dependencies import get_tenant_context
from fastapi import (APIRouter, 
                     Depends, 
                     HTTPException, 
                     Query, 
                     Response, 
                     status,
)
from sqlmodel import Session

from db import get_session
from errors import (ConflictError, 
                    OrderNotFoundError, 
                    CustomerNotFoundError, 
                    DataIntegrityError,
                    InvalidOrderUpdateError,
                    InvalidOrderStateTransitionError)
from mappers import (
    to_order_public, to_organization_public)

#     to_order_detail_public,
#     to_order_detail_with_items_public,
#     to_order_public_list
# )
from models import (
    OrderCreate,
    OrderPublic,
    OrderDetailPublic,
    OrderDetailWithItemsPublic,
    OrderUpdate,
     OrderSortBy, OrderSortDirection, OrderStatus,
     ItemForOrderWithItemsCreate, 
     OrderWithItemsCreate,
     OrderUpdatePatch,
     OrderStatusCountPublic,
     Organization,
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
    current_user: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    db_organization = create_self_service_organization_service(
        name=organization.name,
        actor_user_id=current_user.user_id,
        session=session,
    )

    return to_organization_public(
        db_organization
    )


