# from typing import Annotated, Literal
# from app.auth.dependencies import AuthContext, get_authenticated_user
# from app.tenancy.context import TenantContext
# from app.tenancy.dependencies import get_tenant_context
# from fastapi import (APIRouter, 
#                      Depends, 
#                      HTTPException, 
#                      Query, 
#                      Response, 
#                      status,
#                      Path,  
#     )
# from sqlmodel import Session

# from app.db import get_session

# from app.schemas import (
#     GatePublic,
#     GateStateTransitionRequest,
#     GateCreateRequest,
#     GateSortBy,
#     GateSortDirection,
#     GateWithRequirementsPublic,
#     GatePatchRequest,
#     GateListPublicWithCount

# )

# from app.enums import GateStatusType, GateType

# from app.services.gates import (
#     create_gate_with_requirements_service,
#     get_gate_with_requirements_service,
#     list_active_gates_with_count_service,
#     count_active_gates_by_filter,
#     update_gate_patch_service,
#     archive_gate_service,
#     )

# from app.services.gate_transitions import (
#     transition_gate_state_service,
#     )

# from app.errors import (
#     ConflictError, 
#     GateNotFoundError, 
#     DataIntegrityError,
#     InvalidGateUpdateError,
#     InvalidGateStateTransitionError,
#     InvalidGateStateTransitionError,
#     RejectionReasonRequiredError,
#     GateArchiveNotAllowedError,
#     WorkflowRecordNotFoundError,
#     )

# from app.mappers.gate_mappers import (
#     to_gate_with_requirements_public,
#     to_gate_public,
#     to_gate_list_public_with_count
#     )


# #uses TenantContext which checks whether authenticated user is allowed 
# # to act inside this organization
# #TenantContext depends on the get_authenticated_user
# # TenantContext(
# #     user_id=1,
# #     organization_id=7,
# # )


# router = APIRouter(prefix="/organizations/{organization_id}/workflow-records/{workflow_record_id}/gates", 
#                    tags=["gates"])

# @router.post(
#     "/{gate_id}/state-transitions",
#     response_model=GatePublic,
# )
# def transition_gate_state(*,
#     gate_id: int,
#     workflow_record_id: int,
#     transition: GateStateTransitionRequest,
#     tenant: TenantContext = Depends(get_tenant_context),
#     session: Session = Depends(get_session),
# ):
#     try:
#         db_gate = transition_gate_state_service(
#             tenant=tenant,
#             workflow_record_id=workflow_record_id,
#             gate_id=gate_id,
#             new_status=transition.target_status,
#             reason=transition.reason,
#             session=session,
#         )

#     except GateNotFoundError as error:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=error.detail,
#         ) from error

#     except InvalidGateStateTransitionError as error:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Gate state transition is not allowed",
#         ) from error

#     except DataIntegrityError as error:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Gate state transition could not be completed") from error

#     except RejectionReasonRequiredError as error:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
#             detail="Rejection reason required",
#         ) from error

#     return to_gate_public(db_gate)
