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
from errors import (ConflictError, 
                    GateNotFoundError, 
                    DataIntegrityError,
                    InvalidGateUpdateError,
                    InvalidGateStateTransitionError,
                    InvalidGateStateTransitionError,
                    RejectionReasonRequiredError)
from mappers import (
    to_gate_with_requirements_public,
    to_gate_public)

from models import (
     GatePublic,
     GateType,
     GateStateTransitionRequest,
     GateCreateRequest,
     GateWithRequirementsPublic,
     GateRequirementPublic,
     GateStateTransition,
     GateListPublic
     )

from services.gates import (
    create_gate_with_requirements_service,
    get_gate_with_requirements_service,
    )

from services.gate_transitions import transition_gate_state_service


#     get_order_detail_with_items_service,
#     list_active_orders_service,
#     update_order_service,
#     create_order_with_items_service,
#     update_order_patch_service,
#     archive_order_service,
#     count_active_orders_by_status_service,
# )

router = APIRouter(prefix="/organizations/{organization_id}/gates", 
                   tags=["gates"])



@router.post(
    "",
    response_model=GateWithRequirementsPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_gate(
    gate: GateCreateRequest,
    tenant: TenantContext =
        Depends(get_tenant_context),
    session: Session=
        Depends(get_session),
)-> GateWithRequirementsPublic:
    """create Gate with Requirements"""

    try:
        db_gate, db_requirements = create_gate_with_requirements_service(
            gate_type=gate.gate_type,
            requirement_types=gate.requirement_types,
            tenant=tenant,
            session=session,
        )

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gate could not be created") from error

    public_gate = to_gate_with_requirements_public(db_gate, db_requirements)

    return public_gate


@router.post(
    "/{gate_id}/state-transitions",
    response_model=GatePublic,
)
def transition_gate_state(
    gate_id: int,
    transition: GateStateTransitionRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    session: Session = Depends(get_session),
):
    try:
        db_gate = transition_gate_state_service(
            tenant=tenant,
            gate_id=gate_id,
            new_status=transition.target_status,
            reason=transition.reason,
            session=session,
        )

    except GateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.detail,
        ) from error

    except InvalidGateStateTransitionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gate state transition is not allowed",
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gate state transition could not be completed") from error

    except RejectionReasonRequiredError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Rejection reason required",
        ) from error

    return to_gate_public(db_gate)



@router.get("/{gate_id}", 
            response_model=GateWithRequirementsPublic
            )
def read_gate(
    gate_id: int,
    tenant: TenantContext = 
        Depends(get_tenant_context),
    session: Session = 
    Depends(get_session),
    ) -> GateWithRequirementsPublic:

    try:
        db_gate, db_requirements = get_gate_with_requirements_service(
            gate_id=gate_id,
            tenant=tenant,
            session=session,
        )

    except GateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=error.detail
            ) from error

    return to_gate_with_requirements_public(
        db_gate, 
        db_requirements)





# @router.get("", 
#             response_model=list[OrderPublic])
# def list_orders(
#     status: OrderStatus | None = None,
#     offset: Annotated[int, Query(ge=0)] = 0,
#     limit: Annotated[int, Query(ge=1, le=100)] = 20,
#     session: Session = Depends(get_session),
#     sort_by: OrderSortBy = 'created_at',
#     sort_dir: OrderSortDirection = 'desc'
# ):
#     db_orders = list_active_orders_service(
#         status=status,
#         offset=offset,
#         limit=limit,
#         session=session,
#         sort_by=sort_by,
#         sort_dir=sort_dir,
#     )

#     return to_order_public_list(db_orders)


