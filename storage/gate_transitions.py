from datetime import datetime

from sqlmodel import Session, select, col

from models import Gate, GateStateTransition


def add_gate_state_transition_record(
    *,
    gate_id: int,
    actor_user_id: int,
    previous_status: str,
    new_status: str,
    reason: str | None,
    occurred_at: datetime,
    session: Session,
) -> GateStateTransition:
    db_transition = GateStateTransition(
        gate_id=gate_id,
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
) -> list[GateStateTransition]:
    statement = (
        select(GateStateTransition)
        .join(
            Gate,
            col(GateStateTransition.gate_id) == col(Gate.id),
        )
        .where(
            col(GateStateTransition.gate_id) == order_id,
            col(Gate) == organization_id,
        )
        .order_by(
            col(GateStateTransition.occurred_at),
            col(GateStateTransition.id),
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

