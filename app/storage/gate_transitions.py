from datetime import datetime

from sqlmodel import Session, select, col

from app.models import Gate, GateStatusChange


def add_gate_state_transition_record(
    *,
    gate_id: int,
    gate_submission_id: int,
    actor_user_id: int,
    previous_status: str,
    new_status: str,
    reason: str | None,
    occurred_at: datetime,
    session: Session,
) -> GateStatusChange:
    db_transition = GateStatusChange(
        gate_id=gate_id,
        gate_submission_id=gate_submission_id,
        actor_user_id=actor_user_id,
        previous_status=previous_status,
        new_status=new_status,
        reason=reason,
        occurred_at=occurred_at,
    )

    session.add(db_transition)

    return db_transition


def list_gate_state_transition_records(
    *,
    order_id: int,
    organization_id: int,
    session: Session,
) -> list[GateStatusChange]:
    statement = (
        select(GateStatusChange)
        .join(
            Gate,
            col(GateStatusChange.gate_id) == col(Gate.id),
        )
        .where(
            col(GateStatusChange.gate_id) == order_id,
            col(Gate) == organization_id,
        )
        .order_by(
            col(GateStatusChange.occurred_at),
            col(GateStatusChange.id),
        )
    )

    return list(session.exec(statement).all())

# can also use 
# statement = (
#     select(OrderStateTransition)
#     .join(Order)
#     .where(
#         col(OrderStateTransition.order_id) == order_id,
#         col(Order.organization_id) == organization_id,
#     )
#     .order_by(
#         col(OrderStateTransition.occurred_at),
#         col(OrderStateTransition.id),
#     )
# )


def change_gate_status(
    *,
    db_gate: Gate,
    new_status: str,
    changed_at: datetime,
    session: Session,
) -> Gate:
    
    db_gate.status = new_status
    db_gate.updated_at = changed_at
    db_gate.row_version += 1


    session.add(db_gate)

    return db_gate
