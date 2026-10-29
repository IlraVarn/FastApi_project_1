from datetime import UTC, datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col
from app.tenancy.context import TenantContext
from app.errors import ( GateNotFoundError, 
                    DataIntegrityError, 
                    ConflictError,
                    InvalidGateStateTransitionError,
                    InvalidGateUpdateError,
                    GateArchiveNotAllowedError,
                    WorkflowRecordNotFoundError,
                    StaleGateError
                    )
from app.models import (
    GateSubmission, 
    Gate 
    )
from app.schemas import GateSortBy, GateSortDirection
from app.enums import GateRequirementType, GateStatusType, GateType
from typing import Literal, Any
from sqlalchemy import asc, desc
from app.storage.gates import (
                    add_gate_record, 
                    get_active_gate_by_id,
                    list_active_gates,
                    count_active_gates_by_filter,
                    update_gate_patch,
                    get_gate_by_id_include_archived_for_update,
                    archive_gate_record,
                    get_active_gate_by_id_for_update,
                            )

from app.storage.gate_submissions import (
    get_next_gate_submission_number,
    add_gate_submission, 
    list_evidence_uses_by_gate_id,
    add_gate_submission_evidence,
)

from app.storage.gate_transitions import (
    add_gate_state_transition_record,
    change_gate_status,
)

from app.storage.requirements import (add_gate_requirement_record,
                           list_requirements_by_gate_id,)
from app.storage.workflow_record import get_active_workflow_record_by_id


from sqlmodel import Session, select
from sqlalchemy import func

from app.models.gates.gate_submission import (
    GateSubmission,
    GateSubmissionEvidence,
)
from app.models.evidence.evidence_use import EvidenceUse
from app.models import GateRequirement




def submit_gate_service(
    *,
    gate_id: int,
    workflow_record_id: int,
    expected_row_version: int,
    tenant: TenantContext,
    session: Session,
) -> GateSubmission:

    try:
        # 1. Get current Gate and lock it.
        db_gate = get_active_gate_by_id_for_update(
            gate_id=gate_id,
            workflow_record_id=workflow_record_id,
            organization_id=tenant.organization_id,
            session=session,
        )

        if db_gate is None:
            raise GateNotFoundError()

        # 2. Make sure user submitted the version they actually saw.
        if db_gate.row_version != expected_row_version:
            raise StaleGateError()

        # 3. Gate can only be submitted from DRAFT.
        if db_gate.status != GateStatusType.DRAFT.value:
            raise InvalidGateStateTransitionError()

        # 4. Determine this submission's number.
        submission_number = get_next_gate_submission_number(
            gate_id=gate_id,
            session=session,
        )

        # 5. Create GateSubmission.
        db_submission = add_gate_submission(
            gate_id=gate_id,
            submission_number=submission_number,
            submitted_by_user_id=tenant.user_id,
            session=session,
        )

        # We need its database-generated ID before creating
        # GateSubmissionEvidence children.
        session.flush()

        submission_id = db_submission.id

        if submission_id is None:
            raise DataIntegrityError()

        # 6. Read the Gate's current EvidenceUse assignments.
        db_evidence_uses = list_evidence_uses_by_gate_id(
            gate_id=gate_id,
            session=session,
        )

        # 7. Copy them into immutable submission snapshot rows.
        for evidence_use in db_evidence_uses:
            add_gate_submission_evidence(
                gate_submission_id=submission_id,
                gate_requirement_id=evidence_use.gate_requirement_id,
                evidence_version_id=evidence_use.evidence_version_id,
                session=session,
            )

        changed_at = datetime.now(UTC)

        # 8. Change Gate:
        # DRAFT -> SUBMITTED
        change_gate_status(
            db_gate=db_gate,
            new_status=GateStatusType.SUBMITTED.value,
            changed_at=changed_at,
            session=session,
        )

        # 9. Record history of that status change.
        add_gate_state_transition_record(
            gate_id=gate_id,
            gate_submission_id=submission_id,
            actor_user_id=tenant.user_id,
            previous_status=GateStatusType.DRAFT.value,
            new_status=GateStatusType.SUBMITTED.value,
            reason=None,
            occurred_at=changed_at,
            session=session,
        )

        # 10. Save EVERYTHING together.
        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_submission)

    return db_submission


# The complete flow is therefore:
        # User clicks Submit
        #         ↓
        # lock Gate
        #         ↓
        # check expected row_version
        #         ↓
        # check Gate is DRAFT
        #         ↓
        # calculate submission #1/#2/#3...
        #         ↓
        # create GateSubmission
        #         ↓
        # flush → obtain submission ID
        #         ↓
        # read current EvidenceUse rows
        #         ↓
        # copy them to GateSubmissionEvidence
        #         ↓
        # Gate DRAFT → SUBMITTED
        # row_version + 1
        #         ↓
        # create Gate status-history row
        #         ↓
        # ONE COMMIT