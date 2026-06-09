from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from db import get_session
from errors import NotFoundError, ConflictError
from mappers import (
    to_order_public,
    to_order_detail_public,
    to_order_detail_with_items_public,
    to_order_public_list
)
from models import (
    OrderCreate,
    OrderPublic,
    OrderDetailPublic,
    OrderDetailWithItemsPublic,
    OrderUpdate,
)
from services.orders import (
    create_order_service,
    get_order_detail_service,
    get_order_detail_with_items_service,
    list_orders_service,
    update_order_service,
    delete_order_service,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderPublic)
def create_order(
    order: OrderCreate,
    session: Session = Depends(get_session),
):
    try:
        db_order = create_order_service(
            order_create=order,
            session=session,
        )
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail)

    return to_order_public(db_order)


@router.get("/{order_id}", response_model=OrderDetailPublic)
def read_order(
    order_id: int,
    session: Session = Depends(get_session),
    ):
    try:
        db_order, db_customer = get_order_detail_service(
            order_id=order_id,
            session=session,
        )
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail)

    return to_order_detail_public(db_order, db_customer)


@router.get("/{order_id}/items", response_model=OrderDetailWithItemsPublic)
def read_order_with_items(
    order_id: int,
    session: Session = Depends(get_session),
):
    try:
        db_order, db_customer, db_items = get_order_detail_with_items_service(
            order_id=order_id,
            session=session,
        )
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail)

    return to_order_detail_with_items_public(
        db_order=db_order,
        db_customer=db_customer,
        db_items=db_items,
    )


@router.get("", response_model=list[OrderPublic])
def list_orders(
    status: Annotated[str | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    session: Session = Depends(get_session),
):
    db_orders = list_orders_service(
        status=status,
        offset=offset,
        limit=limit,
        session=session,
    )

    return to_order_public_list(db_orders)


@router.put("/{order_id}", response_model=OrderDetailPublic)
def update_order(
    order_id: int,
    order: OrderUpdate,
    session: Session = Depends(get_session),
):
    try:
        db_order, db_customer = update_order_service(
            order_id=order_id,
            order_update=order,
            session=session,
        )
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail)

    return to_order_detail_public(db_order, db_customer)


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    session: Session = Depends(get_session),
):
    try:
        delete_order_service(
            order_id=order_id,
            session=session,
        )
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail)
    
    except ConflictError as error:
        raise HTTPException(status_code=409, detail=error.detail)

    return {"ok": True}