from typing import Annotated, Literal
from auth.dependencies import AuthContext, get_authenticated_user
from tenancy.context import TenantContext
from tenancy.dependencies import get_tenant_context
from fastapi import (APIRouter, 
                     Depends, 
                     HTTPException, 
                     Query, 
                     Response, 
                     status,
)
from sqlmodel import Session

from db import get_session
from errors import (ConflictError, 
                    OrderNotFoundError, 
                    CustomerNotFoundError, 
                    DataIntegrityError,
                    InvalidOrderUpdateError,
                    InvalidOrderStateTransitionError,
                    InvalidOrderStateTransitionError)
from mappers import (
    to_order_public,)

#     to_order_detail_public,
#     to_order_detail_with_items_public,
#     to_order_public_list
# )
from models import (
    OrderCreate,
    OrderPublic,
    #OrderDetailWithItemsPublic,
    OrderUpdate,
     OrderSortBy, OrderSortDirection, OrderStatus,
     ItemForOrderWithItemsCreate, 
     OrderWithItemsCreate,
     OrderUpdatePatch,
     OrderStatusCountPublic,
     OrderStateTransitionRequest,
     )

from services.orders import (
    create_order_service,
    get_order_service,
    )

from services.order_transitions import transition_order_state_service


#     get_order_detail_with_items_service,
#     list_active_orders_service,
#     update_order_service,
#     create_order_with_items_service,
#     update_order_patch_service,
#     archive_order_service,
#     count_active_orders_by_status_service,
# )


router = APIRouter(prefix="/organizations/{organization_id}/orders", 
                   tags=["orders"])


@router.post(
    "",
    response_model=OrderPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order: OrderCreate,
    tenant: TenantContext =
        Depends(get_tenant_context),
    session: Session=
        Depends(get_session),
):
    try:
        db_order = create_order_service(
        tenant=tenant,
        total_cents=order.total_cents,
        session=session,
    )

    except DataIntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order could not be created") from error

    return to_order_public(db_order)


@router.get("/{order_id}", 
            response_model=OrderPublic
            )
def read_order(
    order_id: int,
    tenant: TenantContext = 
    Depends(get_tenant_context),
    session: Session = Depends(get_session),
    ):

    try:
        db_order = get_order_service(
            order_id=order_id,
            tenant=tenant,
            session=session,
        )

    except OrderNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error

    return to_order_public(db_order)


@router.post(
    "/{order_id}/state_transitions",
    response_model=OrderPublic,
)
def transition_order(
    order_id: int,
    transition: OrderStateTransitionRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    session: Session = Depends(get_session),
):
    try:
        db_order = transition_order_state_service(
            tenant=tenant,
            order_id=order_id,
            new_status=transition.target_status,
            reason=transition.reason,
            session=session,
        )

    except OrderNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.detail,
        ) from error

    except InvalidOrderStateTransitionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order transition is not allowed",
        ) from error

    return to_order_public(db_order)




# @router.post("/with-items",
#     response_model=OrderDetailWithItemsPublic,
#     status_code=201,
# )
# def create_order_with_items(
#     order: OrderWithItemsCreate,
#     current_user: AuthContext = Depends(get_current_user),
#     session: Session = Depends(get_session),
# ) -> OrderDetailWithItemsPublic:
    
#     try:
#         db_order, db_customer, db_items = create_order_with_items_service(
#             customer_id=order.customer_id,
#             owner_id=current_user.user_id,
#             status=order.status,
#             items=order.items,
#             session=session,
#         )

#     except CustomerNotFoundError as error:
#         raise HTTPException(
#             status_code=404,
#             detail=error.detail,
#         ) from error

#     except DataIntegrityError as error:
#         raise HTTPException(
#             status_code=500,
#             detail="internal server error",
#         ) from error

#     return to_order_detail_with_items_public(
#         db_order=db_order,
#         db_customer=db_customer,
#         db_items=db_items
#     )


# @router.get("/summary/status-counts",
#     response_model=list[OrderStatusCountPublic],
# )
# def get_order_status_counts(
#     session: Session = Depends(get_session),
# ) -> list[OrderStatusCountPublic]:
    
#     counts = count_active_orders_by_status_service(                                
#         session=session,
#     )

#     response: list[OrderStatusCountPublic] = []

#     for status_value, order_count in counts:
#         response.append(
#             OrderStatusCountPublic(
#                 status=status_value,
#                 count=order_count,
#             )
#         )

#     return response




# @router.get("/{order_id}/detail", 
#             response_model=OrderDetailWithItemsPublic)
# def read_order_with_items(
#     order_id: int,
#     session: Session = Depends(get_session),
# ):
#     try:
#         db_order, db_customer, db_items = get_order_detail_with_items_service(
#             order_id=order_id,
#             session=session,
#         )

#     except OrderNotFoundError as error:
#         raise HTTPException(status_code=404, detail=error.detail) from error
    
#     except DataIntegrityError as error:
#         raise HTTPException(status_code=500, detail='internal server error') from error

#     return to_order_detail_with_items_public(
#         db_order=db_order,
#         db_customer=db_customer,
#         db_items=db_items,
#     )




# @router.get("", 
#             response_model=list[OrderPublic])
# def list_orders(
#     status: OrderStatus | None = None,
#     offset: Annotated[int, Query(ge=0)] = 0,
#     limit: Annotated[int, Query(ge=1, le=100)] = 20,
#     session: Session = Depends(get_session),
#     sort_by: OrderSortBy = 'created_at',
#     sort_dir: OrderSortDirection = 'desc'
# ):
#     db_orders = list_active_orders_service(
#         status=status,
#         offset=offset,
#         limit=limit,
#         session=session,
#         sort_by=sort_by,
#         sort_dir=sort_dir,
#     )

#     return to_order_public_list(db_orders)


# @router.patch(
#     "/{order_id}",
#     response_model=OrderDetailPublic,
# )
# def patch_order(
#     order_id: int,
#     order_update: OrderUpdatePatch,
#     session: Session = Depends(get_session),
# ) -> OrderDetailPublic:
#     """Partially update one order and return its updated public state."""

#     #convert request model into a dict
#     update_data = order_update.model_dump(
#             exclude_unset=True,
#         )
    
#     try:
#         db_order, db_customer = update_order_patch_service(
#             order_id=order_id,
#             update_data=update_data,
#             session=session,
#         )

#     except OrderNotFoundError as error:
#         raise HTTPException(
#             status_code=404,
#             detail=error.detail,
#         ) from error

#     except InvalidOrderUpdateError as error:
#         raise HTTPException(
#             status_code=400,
#             detail=error.detail,
#         ) from error

#     except InvalidOrderStateTransitionError as error:
#         raise HTTPException(
#             status_code=409,
#             detail=error.detail,
#         ) from error

#     except DataIntegrityError as error:
#         raise HTTPException(
#             status_code=500,
#             detail="internal server error",
#         ) from error

#     return to_order_detail_public(
#         db_order=db_order,
#         db_customer=db_customer,
#     )


# @router.delete("/{order_id}", status_code=204)
# def archive_order(
#     order_id: int,
#     session: Session = Depends(get_session),
# ) -> Response:
#     """Archive one order and return no response body."""

#     try:
#         archive_order_service(
#             order_id=order_id,
#             session=session,
#         )

#     except OrderNotFoundError as error:
#         raise HTTPException(
#             status_code=404,
#             detail=error.detail,
#         ) from error

#     except InvalidOrderStateTransitionError as error:
#         raise HTTPException(
#             status_code=409,
#             detail=error.detail
#             ) from error
    
#     except DataIntegrityError as error:
#         raise HTTPException(
#             status_code=500,
#             detail="internal server error",
#         ) from error

#     return Response(
#         status_code=204,
#     )


