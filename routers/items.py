# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlmodel import Session, select
# from sqlalchemy import desc
# from datetime import datetime, UTC
# from mappers import to_item_public
# from errors import ItemNotFoundError, DataIntegrityError, OrderNotFoundError

# from db import get_session
# from models import (OrderItemPublic, OrderItemCreate)
# from mappers import to_item_public, to_item_public_list
# from typing import Annotated
# from services.items import (create_item_service, 
#                             list_items_service, 
#                             ItemSortBy,
#                             ItemsSortDirection)

# router = APIRouter(prefix="/items", tags=["items"])

# @router.post("", response_model=OrderItemPublic, status_code=201)
# def create_item(item: OrderItemCreate, session: Session = Depends(get_session)):

#     try:
#         db_item = create_item_service(
#             order_id=item.order_id,
#             product_name=item.product_name,
#             quantity=item.quantity,
#             unit_price_cents= item.unit_price_cents,
#             session=session
#             )

#     except OrderNotFoundError as error:
#         raise HTTPException(status_code=404, detail=error.detail) from error
    
#     except DataIntegrityError as error:
#         raise HTTPException(status_code=500, detail='internal server error') from error
    
#     return(to_item_public(db_item))


# @router.get('', response_model=list[OrderItemPublic])
# def list_items(
#     order_id: Annotated[int | None, Query(ge=1)] = None,
#     min_quantity: Annotated[int | None, Query(qe=1)] = None,
#     offset: Annotated[int, Query(ge=0)] = 0,
#     limit: Annotated[int, Query(ge=1, le=50)] = 25,
#     sort_by: ItemSortBy = 'product_name',
#     sort_dir: ItemsSortDirection = 'desc',
#     session: Session = Depends(get_session)
# ):

#     db_items = list_items_service(
#         order_id = order_id,
#         min_quantity = min_quantity,
#         offset=offset,
#         limit=limit,
#         sort_by=sort_by,
#         sort_dir=sort_dir,
#         session=session
#     )

#     return to_item_public_list(db_items)

   
