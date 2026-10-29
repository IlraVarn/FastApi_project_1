
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
    GateSubmissionCreateRequest,
    GateSubmissionPublic
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

# from app.services.gate_transitions import (
#     transition_gate_state_service,
#     )

from app.services.gate_submission import submit_gate_service

from app.errors import (
    ConflictError, 
    GateNotFoundError, 
    DataIntegrityError,
    InvalidGateUpdateError,
    InvalidGateStateTransitionError,
    InvalidGateStateTransitionError,
    RejectionReasonRequiredError,
    GateArchiveNotAllowedError,
    WorkflowRecordNotFoundError,
    StaleGateError
    )

from app.mappers.gate_submission_mappers import (
    to_gate_submission_public
    )


router = APIRouter(
    prefix="/organizations/{organization_id}/workflow-records/{workflow_record_id}/gates",
    tags=["gate_submissions"],
)


@router.post(
    "/{gate_id}/submissions",
    response_model=GateSubmissionPublic,
    status_code=status.HTTP_201_CREATED,
)
def submit_gate(
    *,
    gate_id: int = Path(gt=0),
    workflow_record_id: int = Path(gt=0),
    submission: GateSubmissionCreateRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    session: Session = Depends(get_session),
) -> GateSubmissionPublic:

    try:
        db_submission = submit_gate_service(
            gate_id=gate_id,
            workflow_record_id=workflow_record_id,
            expected_row_version=submission.expected_row_version,
            tenant=tenant,
            session=session,
        )

    except GateNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.detail,
        ) from error

    except StaleGateError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gate has changed since it was loaded",
        ) from error

    except InvalidGateStateTransitionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gate cannot be submitted from its current status",
        ) from error

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gate submission could not be completed",
        ) from error

    return to_gate_submission_public(db_submission)