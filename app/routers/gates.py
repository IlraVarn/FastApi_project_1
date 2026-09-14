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
                     Path,  
    )
from sqlmodel import Session

from app.db import get_session

from app.schemas import (
    GatePublic,
    GateStateTransitionRequest,
    GateCreateRequest,
    GateSortBy,
    GateSortDirection,
    GateWithRequirementsPublic,
    GatePatchRequest,
    GateListPublicWithCount

)

from app.enums import GateStatusType, GateType

from app.services.gates import (
    create_gate_with_requirements_service,
    get_gate_with_requirements_service,
    list_active_gates_with_count_service,
    count_active_gates_by_filter,
    update_gate_patch_service,
    archive_gate_service,
    )

from app.services.gate_transitions import (
    transition_gate_state_service,
    )

from app.errors import (
    ConflictError, 
    GateNotFoundError, 
    DataIntegrityError,
    InvalidGateUpdateError,
    InvalidGateStateTransitionError,
    InvalidGateStateTransitionError,
    RejectionReasonRequiredError,
    GateArchiveNotAllowedError,
    )

from app.mappers.gate_mappers import (
    to_gate_with_requirements_public,
    to_gate_public,
    to_gate_list_public_with_count
    )


#uses TenantContext which checks whether authenticated user is allowed 
# to act inside this organization
#TenantContext depends on the get_authenticated_user
# TenantContext(
#     user_id=1,
#     organization_id=7,
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

    return to_gate_with_requirements_public(db_gate, db_requirements)



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


#GET AND LIST
@router.get("/{gate_id}", 
            response_model=GateWithRequirementsPublic
            )
def get_gate_with_requirements(
    gate_id: int = Path(gt=0),
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


@router.get("", 
            response_model=GateListPublicWithCount)
def list_gates_with_count(
    gate_type: GateType | None = None,
    status: GateStatusType | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    session: Session = Depends(get_session),
    sort_by: GateSortBy = 'created_at',
    sort_dir: GateSortDirection = 'desc',
    tenant: TenantContext =
        Depends(get_tenant_context)
) -> GateListPublicWithCount:
    
    db_gates, db_gates_count = list_active_gates_with_count_service(
        gate_type=gate_type,
        status=status,
        offset=offset,
        limit=limit,
        session=session,
        sort_by=sort_by,
        sort_dir=sort_dir,
        tenant=tenant
    )

    return to_gate_list_public_with_count(
        db_gates=db_gates,
        count=db_gates_count)



#UPDATE    
@router.patch(
    "/{gate_id}",
    response_model=GatePublic,
)
def patch_gate(
    gate_id: int,
    gate_update: GatePatchRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    session: Session = Depends(get_session),
) -> GatePublic:
    """Partially update one gate and return its updated public state."""

    #convert request model into a dict
    update_data = gate_update.model_dump(
            exclude_unset=True,
        )
    
    try:
        db_gate = update_gate_patch_service(
            gate_id=gate_id,
            tenant=tenant,
            update_data=update_data,
            session=session,
        )

    except GateNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=error.detail,
        ) from error

    except InvalidGateUpdateError as error:
        raise HTTPException(
            status_code=400,
            detail=error.detail,
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        ) from error

    return to_gate_public(
        db_gate=db_gate,

    )


#DELETE

@router.delete("/{gate_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_gate(
    gate_id: int,
    tenant: TenantContext =
            Depends(get_tenant_context),
    session: Session = Depends(get_session),
) -> Response:
    """Archive one gate and return no response body."""

    try:
        archive_gate_service(
            gate_id=gate_id,
            tenant=tenant,
            session=session,
        )

    except GateNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=error.detail,
        ) from error

    except GateArchiveNotAllowedError as error:
        raise HTTPException(
            status_code=409,
            detail=error.detail
            ) from error
    
    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        ) from error

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


