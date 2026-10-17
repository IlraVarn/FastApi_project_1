from sqlmodel import Session, select, col
from sqlalchemy import asc, desc, func
from datetime import UTC, datetime
from app.models import (
    Gate, 
    GateStateTransition
    )

from app.enums import GateStatusType, GateType
from app.schemas import GateSortBy, GateSortDirection

from typing import Any

GATE_SORT_COLUMNS = {
    "created_at": Gate.created_at,
    "status": Gate.status,
    "id": Gate.id,
}




def add_gate_record(
    *,
    organization_id: int,
    gate_type: GateType,
    status: GateStatusType,
    session: Session,
) -> Gate:
    """Create and stage a new Gate for persistence.

    Gate model defaults initialize created_at and updated_at.
    Does not commit, rollback, or refresh.
    """
    db_gate = Gate(
        organization_id=organization_id,
        gate_type=gate_type.value,
        status=status.value,
    )

    session.add(db_gate)

    return db_gate


def get_active_gate_by_id(
    *,
    gate_id: int,
    organization_id: int,
    session: Session,
) -> Gate | None:

    """Return an active Gate by ID, or None if missing or archived."""

    statement = (
        select(Gate)
        .where(
        col(Gate.id) == gate_id,
            Gate.organization_id == organization_id,
            col(Gate.archived_at).is_(None),
        ))

    return session.exec(statement).first()


def get_gate_by_id_include_archived(
    *,
    gate_id: int,
    organization_id: int,
    session: Session,
) -> Gate | None:

    """Return Gate by ID, include archived."""

    statement = (
        select(Gate)
        .where(
        col(Gate.id) == gate_id,
        col(Gate.organization_id == organization_id,
        )))

    return session.exec(statement).first()

#former update_gate_status_record
def change_gate_status(
    *,
    db_gate: Gate,
    new_status: str,
    changed_at: datetime,
    session: Session,
) -> Gate:
    
    db_gate.status = new_status
    db_gate.updated_at = changed_at

    session.add(db_gate)

    return db_gate


def list_active_gates(
        *,
        session: Session,    
        gate_type: GateType | None,          
        status: GateStatusType | None,
        sort_by: GateSortBy,
        sort_dir: GateSortDirection,
        offset: int,
        limit: int,
        organization_id: int
    )-> list[Gate]:
    """Return filtered, sorted, active gates within 
        one result page."""
    
    statement = (select(Gate)
        .where(
            Gate.organization_id == organization_id,
            col(Gate.archived_at).is_(None)))

    if status is not None:
        statement = statement.where(
            col(Gate.status == status.value))

    if gate_type is not None:
        statement = statement.where(
            Gate.gate_type == gate_type.value)

    sort_column = GATE_SORT_COLUMNS[sort_by]

    if sort_dir == "desc":
        primary_sort = desc(sort_column)
        tie_breaker = desc(col(Gate.id))
    else:
        primary_sort = asc(sort_column)
        tie_breaker = asc(col(Gate.id))

    if sort_by == "id":
        statement = statement.order_by(primary_sort)
    else:
        statement = statement.order_by(
            primary_sort, 
            tie_breaker)

    statement = statement.offset(offset).limit(limit)

    db_gates = list(session.exec(statement).all())

    return db_gates


def count_active_gates_by_filter(
        *,
        session: Session,    
        gate_type: GateType | None,          
        status: GateStatusType | None,
        organization_id: int
) -> int:
    """Return the number of active gates by filter."""

    statement = (
        select(
            func.count(col(Gate.id)),
        )
         .where(
            Gate.organization_id == organization_id,
            col(Gate.archived_at).is_(None)))

    if status is not None:
        statement = statement.where(
            col(Gate.status == status.value))

    if gate_type is not None:
        statement = statement.where(
            Gate.gate_type == gate_type.value)

    total_count = session.exec(statement).one()

    return total_count


def update_gate_patch(
    *,
    db_gate: Gate,
    update_data: dict[str, Any],
    session: Session,
) -> Gate:
    """Apply validated fields to an existing Gate,
    set updated_at to the current UTC time,
    and stage it for persistence.

    Does not commit, rollback, or refresh.
    """

    db_gate.sqlmodel_update(update_data)
    db_gate.updated_at= datetime.now(UTC)
    session.add(db_gate)

    return db_gate


def archive_gate_record(
    *,
    db_gate: Gate,
    session: Session,
) -> Gate:
    
    """Set an Gate's archive timestamp and stage it for persistence.

    Does not commit, rollback, refresh, or decide whether archiving is allowed.
    """

    now = datetime.now(UTC)

    db_gate.archived_at = now
    db_gate.updated_at = now

    session.add(db_gate)

    return db_gate


# def group_active_gates_by_filter(
#         *,
#         session: Session,    
#         gate_type: GateType | None,          
#         status: GateStatus | None,
#         organization_id: int
# ) -> list[tuple[str, int]]:
#     """Return the number of active gates in each status."""

#     statement = (
#         select(
#             col(Gate.status),
#             func.count(col(Gate.id)),
#         )
#         .where(
#             col(Gate.archived_at).is_(None),
#         )
#         .group_by(
#             col(Gate.status),
#         )
#         .order_by(
#             col(Gate.status),
#         )
#     )

#     rows = session.exec(statement).all()

#     result: list[tuple[str, int]] = []

#     for status_value, order_count in rows:
#         result.append(
#             (
#                 status_value,
#                 int(order_count),
#             )
#         )

#     return result


# #JOIN
# def list_order_customer_pairs(
#     session: Session,
# ) -> list[tuple[Order, Customer]]:
#     """Return every order together with its referenced customer."""

#     statement = (
#         select(Order, Customer)
#         .join(
#             Customer,
#             col(Customer.id) == Order.customer_id,
#         )
#         .where(col(Order.archived_at).is_(None),)
#         .order_by(
#             desc(col(Order.created_at)),
#             desc(col(Order.id)),
#         )
#     )

#     result = session.exec(statement)

#     return list(result.all())

