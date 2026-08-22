from datetime import datetime

from sqlmodel import Session, select, col

from models import Order, OrderStateTransition


def add_order_transition_record(
    *,
    order_id: int,
    actor_user_id: int,
    previous_status: str,
    new_status: str,
    reason: str | None,
    occurred_at: datetime,
    session: Session,
) -> OrderStateTransition:
    db_transition = OrderStateTransition(
        order_id=order_id,
        actor_user_id=actor_user_id,
        previous_status=previous_status,
        new_status=new_status,
        reason=reason,
        occurred_at=occurred_at,
    )

    session.add(db_transition)

    return db_transition


def list_order_transition_records(
    *,
    order_id: int,
    organization_id: int,
    session: Session,
) -> list[OrderStateTransition]:
    statement = (
        select(OrderStateTransition)
        .join(
            Order,
            col(OrderStateTransition.order_id) == col(Order.id),
        )
        .where(
            col(OrderStateTransition.order_id) == order_id,
            col(Order.organization_id) == organization_id,
        )
        .order_by(
            col(OrderStateTransition.occurred_at),
            col(OrderStateTransition.id),
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

