from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.errors import (
    DataIntegrityError,
    InvalidGateStateTransitionError,
    GateNotFoundError,
    RejectionReasonRequiredError
)
from app.models import Gate
from app.enums import GateStatusType
from app.storage.gate_transitions import add_gate_state_transition_record
from app.storage.gates import (
    get_active_gate_by_id,
    change_gate_status,
)
from app.tenancy.context import TenantContext


ALLOWED_GATE_TRANSITIONS: dict[GateStatusType, set[GateStatusType]] = {
    GateStatusType.DRAFT: {
        GateStatusType.SUBMITTED,
    },
    GateStatusType.SUBMITTED: {
        GateStatusType.APPROVED,
        GateStatusType.REJECTED,
    },
    GateStatusType.APPROVED: set(),
    GateStatusType.REJECTED: {
        GateStatusType.DRAFT,
    },
}


def transition_gate_state_service(
    *,
    tenant: TenantContext,
    gate_id: int,
    new_status: GateStatusType,
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
        current_status = GateStatusType(db_gate.status)

    except ValueError as error:
        raise DataIntegrityError() from error

    allowed_next_states = ALLOWED_GATE_TRANSITIONS[current_status]

    if new_status not in allowed_next_states:
        raise InvalidGateStateTransitionError()

    changed_at = datetime.now(UTC)

    if (
        new_status == GateStatusType.REJECTED
        and reason is None
    ):
        raise RejectionReasonRequiredError()
    
    if db_gate.id is None:
        raise DataIntegrityError()

    try:
        change_gate_status(
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


