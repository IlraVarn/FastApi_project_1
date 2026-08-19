from datetime import UTC, datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, col
from tenancy.context import TenantContext
from errors import (CustomerNotFoundError, 
                    OrderNotFoundError, 
                    DataIntegrityError, 
                    ConflictError,
                    InvalidOrderStateTransitionError,
                    InvalidOrderUpdateError,)
from models import (Order, OrderCreate, OrderItem, OrderUpdate, 
                    OrderSortDirection, OrderSortBy, OrderStatus,
                    ItemForOrderWithItemsCreate,
                    OrderUpdatePatch)
from typing import Literal, Any
from sqlalchemy import asc, desc
from storage.orders import (add_order_record, 
                            get_active_order_by_id,
                            )

                            # update_order,
                            # list_active_orders,
                            # list_orders_by_customer_id,
                            # update_order_patch,
                            # get_order_by_id_include_archived,
                            # archive_order_record,
                            # count_active_orders_by_status,
                            # )
from storage.items import list_items_by_order_id, create_item_record



def create_order_service(
    *,
    tenant: TenantContext,
    total_cents: int,
    status: str,
    session: Session,
) -> Order:
    db_order = add_order_record(
        organization_id=tenant.organization_id,
        total_cents=total_cents,
        status=status,
        session=session,
    )

    try:
        session.commit()

    except IntegrityError as error:
        session.rollback()
        raise DataIntegrityError() from error
    
    except Exception:
        session.rollback()
        raise

    session.refresh(db_order)

    return db_order


def get_order_service(*,
    tenant: TenantContext,
    order_id: int,
    session: Session,
) -> Order:
    
    db_order = get_active_order_by_id(
        order_id=order_id, 
        organization_id=tenant.organization_id,
        session=session)

    if db_order is None:
        raise OrderNotFoundError()

    return db_order


# def create_order_with_items_service(
#     *,
#     customer_id: int,
#     owner_id: int,
#     status: OrderStatus,
#     items: list[ItemForOrderWithItemsCreate],
#     session: Session,
# ) -> tuple[Order, Customer, list[OrderItem]]:
    
#     db_customer = get_customer_by_id(
#         customer_id=customer_id,
#         session=session,
#     )

#     if db_customer is None:
#         raise CustomerNotFoundError()

#     total_cents = 0

#     for item in items:
#         total_cents += item.quantity * item.unit_price_cents

#     try:
#         db_order = add_order_record(
#             customer_id=customer_id,
#             owner_id=owner_id,
#             total_cents=total_cents,
#             status=status,
#             session=session,
#         )

#         session.flush()

#         order_id = db_order.id

#         #the following defensive check catches the problem at the source. 
#         # Otherwise it surfaces at the end and loos like the items is the problem
#         if order_id is None:
#             session.rollback()
#             raise DataIntegrityError()

#         db_items: list[OrderItem] = []

#         for item in items:
#             db_item = create_item_record(
#                 order_id=order_id,
#                 product_name=item.product_name,
#                 quantity=item.quantity,
#                 unit_price_cents=item.unit_price_cents,
#                 session=session,
#             )

#             db_items.append(db_item)

#         session.commit()

#     except IntegrityError as error:
#         session.rollback()
#         raise DataIntegrityError() from error
#     except Exception:
#         session.rollback()
#         raise

#     #only reached on success
#     session.refresh(db_order)

#     for db_item in db_items:
#         session.refresh(db_item)

#     return db_order, db_customer, db_items




# def get_order_detail_with_items_service(
#     order_id: int,
#     session: Session,
# ) -> tuple[Order, Customer, list[OrderItem]]:
    
#     db_order, db_customer = get_order_detail_service(
#         order_id=order_id,
#         session=session,
#     )

#     db_items = list_items_by_order_id(order_id=order_id, session=session)

#     return db_order, db_customer, db_items


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


