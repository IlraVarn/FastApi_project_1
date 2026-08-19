from sqlmodel import Session, select, col
from sqlalchemy import asc, desc, func
from datetime import UTC, datetime
from models import (Order, OrderItem, OrderUpdate,  OrderStatus, 
                    OrderSortBy, OrderSortDirection)
from models import ORDER_SORT_COLUMNS
from typing import Any



def add_order_record(
    *,
    organization_id: int,
    total_cents: int,
    status: str,
    session: Session,
) -> Order:
    db_order = Order(
        organization_id=organization_id,
        total_cents=total_cents,
        status=status,
    )

    session.add(db_order)

    return db_order


def get_active_order_by_id(
    *,
    order_id: int,
    organization_id: int,
    session: Session,
) -> Order | None:

    """Return an active Order by ID, or None if missing or archived."""

    statement = (
        select(Order)
        .where(
        col(Order.id) == order_id,
            Order.organization_id == organization_id,
            col(Order.archived_at).is_(None),
        ))

    return session.exec(statement).first()


# def add_order_recordd(
#     customer_id: int,
#     owner_id: int,
#     total_cents: int,
#     status: str,
#     session: Session,
#     ) -> Order:

#     """Create and stage a new Order for persistence.

#     Order model defaults initialize created_at and updated_at.
#     Does not commit, rollback, or refresh.
#     """
      
#     db_order = Order(
#         customer_id=customer_id,
#         owner_id=owner_id,
#         total_cents=total_cents,
#         status=status,
#     )

#     session.add(db_order)
#     return db_order




# def get_order_by_id_include_archived(
#     *,
#     order_id: int,
#     session: Session,
#     ) -> Order | None:
    
#     return session.get(Order, order_id)


# def list_active_orders(
#         *,
#         session: Session,               
#         status: OrderStatus | None,
#         sort_by: OrderSortBy,
#         sort_dir: OrderSortDirection,
#         offset: int,
#         limit: int
#     )-> list[Order]:
#     """Return filtered, sorted, active orders within 
#         one result page."""
    
#     statement = select(Order).where(
#         col(Order.archived_at).is_(None))

#     if status is not None:
#         statement = statement.where(Order.status == status)

#     sort_column = ORDER_SORT_COLUMNS[sort_by]

#     if sort_dir == "desc":
#         primary_sort = desc(sort_column)
#         tie_breaker = desc(col(Order.id))
#     else:
#         primary_sort = asc(sort_column)
#         tie_breaker = asc(col(Order.id))

#     if sort_by == "id":
#         statement = statement.order_by(primary_sort)
#     else:
#         statement = statement.order_by(primary_sort, tie_breaker)

#     statement = statement.offset(offset).limit(limit)

#     db_orders = list(session.exec(statement).all())

#     return db_orders


# def list_orders_by_customer_id(
#     customer_id: int,
#     session: Session,
# ) -> list[Order]:
#     """Return all orders belonging to one customer.
#     Orders are returned newest first, with ID as the stable tie-breaker.
#     """

#     statement = (
#         select(Order)
#         .where(
#             col(Order.archived_at).is_(None))
#             .order_by(
#                 desc(col(Order.created_at)),
#                 desc(col(Order.id)),
#         )
#     )

#     result = session.exec(statement)

#     return list(result.all())


# def archive_order_record(
#     *,
#     db_order: Order,
#     session: Session,
# ) -> Order:
    
#     """Set an Order's archive timestamp and stage it for persistence.

#     Does not commit, rollback, refresh, or decide whether archiving is allowed.
#     """

#     now = datetime.now(UTC)

#     db_order.archived_at = now
#     db_order.updated_at = now

#     session.add(db_order)

#     return db_order


# #PATCH ORDER

# def update_order(
#         *,
#         db_order: Order,
#         total_cents: int,
#         status: str,
#         session: Session,
#     ) -> Order:

#     db_order.total_cents = total_cents
#     db_order.status = status


#     session.add(db_order)
#     return db_order


# def update_order_patch(
#     *,
#     db_order: Order,
#     update_data: dict[str, Any],
#     session: Session,
# ) -> Order:
#     """Apply validated fields to an existing Order,
#     set updated_at to the current UTC time,
#     and stage it for persistence.

#     Does not commit, rollback, or refresh.
#     """

#     db_order.sqlmodel_update(update_data)
#     db_order.updated_at= datetime.now(UTC)
#     session.add(db_order)

#     return db_order


# #COUNT
# def count_active_orders_by_status(
#     *,
#     session: Session,
# ) -> list[tuple[str, int]]:
#     """Return the number of active orders in each status."""

#     statement = (
#         select(
#             col(Order.status),
#             func.count(col(Order.id)),
#         )
#         .where(
#             col(Order.archived_at).is_(None),
#         )
#         .group_by(
#             col(Order.status),
#         )
#         .order_by(
#             col(Order.status),
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

