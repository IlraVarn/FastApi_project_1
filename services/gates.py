from datetime import UTC, datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col
from tenancy.context import TenantContext
from errors import ( GateNotFoundError, 
                    DataIntegrityError, 
                    ConflictError,
                    InvalidGateStateTransitionError,
                    InvalidGateUpdateError,)
from models import (Gate, GateType,GateCreateRequest, GateRequirement, 
                    OrderSortDirection, OrderSortBy, GateStatus,
                    ItemForOrderWithItemsCreate, GateRequirementType
                    )
from typing import Literal, Any
from sqlalchemy import asc, desc
from storage.gates import (add_gate_record, 
                            get_active_gate_by_id,
                            )

from storage.items import (add_gate_requirement_record,
                           list_requirements_by_gate_id,)




def create_gate_with_requirements_service(
    *,
    tenant: TenantContext,
    gate_type: GateType,
    requirement_types: list[GateRequirementType],
    session: Session,
) -> tuple[Gate, list[GateRequirement]]:

    try:

        db_gate = add_gate_record(
            organization_id=tenant.organization_id,
            gate_type=gate_type,
            status=GateStatus.DRAFT.value,
            session=session,
        )

        session.flush()

        gate_id = db_gate.id

        if gate_id is None:
            session.rollback()
            raise DataIntegrityError()


        db_requirements: list[GateRequirement] = []

        for requirement_type in requirement_types:
            db_requirement = add_gate_requirement_record(
                gate_id=gate_id,
                requirement_type=requirement_type.value,
                session=session,
            )

            db_requirements.append(db_requirement)

        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error

    except Exception:
        session.rollback()
        raise

    session.refresh(db_gate)

    for db_requirement in db_requirements:
        session.refresh(db_requirement)

    return db_gate, db_requirements

 


# def get_gate_service(*,
#     tenant: TenantContext,
#     gate_id: int,
#     session: Session,
# ) -> Gate:
    
#     db_order = get_active_gate_by_id(
#         gate_id=gate_id, 
#         organization_id=tenant.organization_id,
#         session=session)

#     if db_order is None:
#         raise OrderNotFoundError()

#     return db_order




def get_gate_with_requirements_service(*,
    tenant: TenantContext,                                   
    gate_id: int,
    session: Session,
) -> tuple[Gate, list[GateRequirement]]:

    db_gate = get_active_gate_by_id(
        gate_id=gate_id, 
        organization_id=tenant.organization_id,
        session=session)

    if db_gate is None:
        raise GateNotFoundError()

    db_requirements = list_requirements_by_gate_id(
        gate_id=gate_id, session=session)

    return db_gate, db_requirements


# def update_order_service(
#     order_id: int,
#     total_cents: int,
#     status: str,
#     session: Session,
# ) -> tuple[Order, Customer]:
    
#     db_order = get_active_order_by_id(
#         order_id=order_id, 
#         session=session)

#     if db_order is None:
#         raise OrderNotFoundError()

#     db_customer = get_customer_by_id(customer_id=db_order.customer_id, 
#                                      session=session)
    
#     if db_customer is None:
#         raise DataIntegrityError()
    
#     try:
#         db_order = update_order(db_order=db_order, 
#                             total_cents=total_cents, 
#                             status=status, 
#                             session=session)

#         session.commit()

#     except IntegrityError as error:
#         session.rollback()
#         raise DataIntegrityError() from error

#     session.refresh(db_order)

#     return db_order, db_customer


# def list_active_orders_service(
#         *,
#         session: Session,               
#         status: OrderStatus | None,
#         sort_by: OrderSortBy,
#         sort_dir: OrderSortDirection,
#         offset: int,
#         limit: int,
# ) -> list[Order]:
    
#     db_orders = list_active_orders(
#         session=session,               
#         status=status,
#         sort_by=sort_by,
#         sort_dir=sort_dir,
#         offset=offset,
#         limit=limit)


#     return db_orders


# def update_order_patch_service(
#     *,
#     order_id: int,
#     update_data: dict[str, Any],
#     session: Session,
# ) -> tuple[Order, Customer]:
#     """Partially update an existing order and commit the valid result.

#     Only fields supplied by the client are changed.

#     Raises:
#         OrderNotFoundError: The requested order does not exist.
#         InvalidOrderUpdateError: The request is empty or supplies null.
#         InvalidOrderStateTransitionError: The requested change conflicts
#             with the order's current state.
#         DataIntegrityError: Stored relationships or database writes fail.
#     """

#     db_order = get_active_order_by_id(
#         order_id=order_id,
#         session=session,
#     )

#     if db_order is None:
#         raise OrderNotFoundError()
    
#     db_customer = get_customer_by_id(
#         customer_id=db_order.customer_id,
#         session=session,
#     )

#     if db_customer is None:
#         raise DataIntegrityError()

#     #working with the dict
#     if not update_data:
#         raise InvalidOrderUpdateError()

#     for value in update_data.values():
#         if value is None:   
#             raise InvalidOrderUpdateError()

#     changing_total = (
#         "total_cents" in update_data
#         and update_data["total_cents"] != db_order.total_cents
#     )

#     changing_status = (
#         "status" in update_data
#         and update_data["status"] != db_order.status
#     )

#     if db_order.status == "paid":
#         if changing_total or changing_status:
#             raise InvalidOrderStateTransitionError()

#     try:
#         update_order_patch(
#             db_order=db_order,
#             update_data=update_data,
#             session=session,
#         )

#         session.commit()

#     except IntegrityError as error:
#         session.rollback()
#         raise DataIntegrityError() from error

#     session.refresh(db_order)

#     return db_order, db_customer


# def archive_order_service(
#     *,
#     order_id: int,
#     session: Session,
# ) -> None:
#     """Archive one order.

#     Repeated archive requests for the same existing order succeed 
#     without changing its original archive timestamp.

#     Raises:
#         OrderNotFoundError: No order exists with the requested ID.
#         DataIntegrityError: The database write fails.
#     """

#     db_order = get_order_by_id_include_archived(
#         order_id=order_id,
#         session=session,
#     )

#     if db_order is None:
#         raise OrderNotFoundError()

#     if db_order.archived_at is not None:
#         return

#     if db_order.status == 'pending':
#         raise InvalidOrderStateTransitionError()
    

#     try:
#         archive_order_record(
#             db_order=db_order,
#             session=session,
#         )

#         session.commit()

#     except IntegrityError as error:
#         session.rollback()
#         raise DataIntegrityError() from error


# def count_active_orders_by_status_service(
#     *,
#     session: Session,
# ) -> list[tuple[str, int]]:
#     """Return active order counts grouped by status."""

#     return count_active_orders_by_status(                  
#         session=session,
#     )


