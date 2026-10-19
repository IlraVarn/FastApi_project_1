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
  WorkflowRecordCreateRequest, 
  WorkflowRecordPublic
)



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
    DataIntegrityError,
    )

from app.mappers.gate_mappers import (
    to_gate_with_requirements_public,
    to_gate_public,
    )


#uses TenantContext which checks whether authenticated user is allowed 
# to act inside this organization
#TenantContext depends on the get_authenticated_user
# TenantContext(
#     user_id=1,
#     organization_id=7,
# )


router = APIRouter(prefix="/organizations/{organization_id}/workflow-records", 
                   tags=["workflow_records"])


@router.post(
    "",
    response_model=WorkflowRecordPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow_record(
    workflow_record: WorkflowRecordCreateRequest,
    tenant: TenantContext =
        Depends(get_tenant_context),
    session: Session=
        Depends(get_session),
)-> WorkflowRecordPublic:
    """create WorkflowRecord"""

    try:
        db_workflow_record = create_workflow_record_service(
            reference=workflow_record.reference,
            tenant=tenant,
            session=session,
        )

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WorkflowRecord could not be created",
            ) from error

    return to_workflow_record_public(db_workflow_record)

