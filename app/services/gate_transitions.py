from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.errors import (
    DataIntegrityError,
    InvalidGateStateTransitionError,
    GateNotFoundError,
    RejectionReasonRequiredError
)
from app.models import Gate, GateStatus
from app.storage.gate_transitions import add_gate_state_transition_record
from app.storage.gates import (
    get_active_gate_by_id,
    update_gate_status_record,
)
from app.tenancy.context import TenantContext


ALLOWED_GATE_TRANSITIONS: dict[GateStatus, set[GateStatus]] = {
    GateStatus.DRAFT: {
        GateStatus.SUBMITTED,
    },
    GateStatus.SUBMITTED: {
        GateStatus.APPROVED,
        GateStatus.REJECTED,
    },
    GateStatus.APPROVED: set(),
    GateStatus.REJECTED: {
        GateStatus.DRAFT,
    },
}


def transition_gate_state_service(
    *,
    tenant: TenantContext,
    gate_id: int,
    new_status: GateStatus,
    reason: str | None,
    session: Session,
) -> Gate:
    db_gate = get_active_gate_by_id(
        gate_id=gate_id,
        organization_id=tenant.organization_id,
        session=session,
    )

    if db_gate is None:
        raise GateNotFoundError()

    try:
        current_status = GateStatus(db_gate.status)

    except ValueError as error:
        raise DataIntegrityError() from error

    allowed_next_states = ALLOWED_GATE_TRANSITIONS[current_status]

    if new_status not in allowed_next_states:
        raise InvalidGateStateTransitionError()

    changed_at = datetime.now(UTC)

    if (
        new_status == GateStatus.REJECTED
        and reason is None
    ):
        raise RejectionReasonRequiredError()
    
    if db_gate.id is None:
        raise DataIntegrityError()

    try:
        update_gate_status_record(
            db_gate=db_gate,
            new_status=new_status.value,
            changed_at=changed_at,
            session=session,
        )

        add_gate_state_transition_record(
            gate_id=db_gate.id,
            actor_user_id=tenant.user_id,
            previous_status=current_status.value,
            new_status=new_status.value,
            reason=reason,
            occurred_at=changed_at,
            session=session,
        )

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_gate)

    return db_gate


