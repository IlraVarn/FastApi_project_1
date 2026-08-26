from sqlmodel import Session, select, col
from sqlalchemy import asc, desc
from models import (GateRequirement, 
                  )
from datetime import UTC, datetime



def add_gate_requirement_record(
        *,
        gate_id: int,
        requirement_type: str,
        session: Session
        ) -> GateRequirement:
    db_requirement = GateRequirement(
        gate_id=gate_id,
        requirement_type=requirement_type,
    )
    session.add(db_requirement)

    return db_requirement


def list_requirements_by_gate_id(
        *,
        gate_id: int,
        session: Session
    )-> list[GateRequirement]:
    

    statement = (
        select(GateRequirement)
        .where(GateRequirement.gate_id == gate_id)
        .order_by(col(GateRequirement.id))
    )
    db_requirements = list(session.exec(statement).all())

    return db_requirements


# def list_items_sorted(*,
#     order_id: int | None,
#     min_quantity: int | None,
#     offset: int,
#     limit: int,
#     sort_by: ItemSortBy,
#     sort_dir: ItemsSortDirection,
#     session: Session
# ) -> list[OrderItem] :
    
#     statement = select(OrderItem)

#     if order_id is not None:
#         statement = statement.where(
#             OrderItem.order_id == order_id)

#     if min_quantity is not None:
#         statement = statement.where(
#             OrderItem.quantity >= min_quantity)

#     sort_column = ITEM_SORT_COLUNMS[sort_by]

#     if sort_dir == 'asc':
#         primary_sort = asc(sort_column)
#         tie_breaker = asc(col(OrderItem.id))
#     else:
#         primary_sort = desc(sort_column)
#         tie_breaker = desc(col(OrderItem.id))

#     if sort_by == 'id':
#         statement = statement.order_by(primary_sort)
#     else:
#         statement = statement.order_by(primary_sort, tie_breaker)
    

#     statement = statement.offset(offset).limit(limit)

#     db_items = list(session.exec(statement).all())

#     return db_items


