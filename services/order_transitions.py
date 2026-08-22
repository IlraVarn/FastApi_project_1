from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from errors import (
    DataIntegrityError,
    InvalidOrderTransitionError,
    OrderNotFoundError,
)
from models import Order, OrderStatus
from storage.order_transitions import add_order_transition_record
from storage.orders import (
    get_active_order_by_id,
    update_order_status_record,
)
from tenancy.context import TenantContext


ALLOWED_ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {
        OrderStatus.SUBMITTED,
    },
    OrderStatus.SUBMITTED: {
        OrderStatus.APPROVED,
        OrderStatus.REJECTED,
    },
    OrderStatus.APPROVED: set(),
    OrderStatus.REJECTED: {
        OrderStatus.DRAFT,
    },
}


def transition_order_state_service(
    *,
    tenant: TenantContext,
    order_id: int,
    new_status: OrderStatus,
    reason: str | None,
    session: Session,
) -> Order:
    db_order = get_active_order_by_id(
        order_id=order_id,
        organization_id=tenant.organization_id,
        session=session,
    )

    if db_order is None:
        raise OrderNotFoundError()

    try:
        current_status = OrderStatus(db_order.status)
    except ValueError as error:
        raise DataIntegrityError() from error

    allowed_next_states = ALLOWED_ORDER_TRANSITIONS[current_status]

    if new_status not in allowed_next_states:
        raise InvalidOrderStateTransitionError()

    changed_at = datetime.now(UTC)

    cleaned_reason = reason.strip() if reason is not None else None

    if cleaned_reason == "":
        cleaned_reason = None

    if db_order.id is None:
        raise DataIntegrityError()

    try:
        update_order_status_record(
            db_order=db_order,
            new_status=new_status.value,
            changed_at=changed_at,
            session=session,
        )

        add_order_transition_record(
            order_id=db_order.id,
            actor_user_id=tenant.user_id,
            previous_status=current_status.value,
            new_status=new_status.value,
            reason=cleaned_reason,
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

    session.refresh(db_order)

    return db_order
