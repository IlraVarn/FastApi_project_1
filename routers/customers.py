# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlmodel import Session, select
# from sqlalchemy import desc
# from typing import Annotated


# from db import get_session
# from models import (CustomerPublic, 
#                     Customer, 
#                     CustomerCreate,
#                     CustomerSortDirection, 
#                     CustomerSortBy,
#                     OrderSummaryPerCustomerPublic,
#                     CustomerWithOrdersPublic
#                     )

# from mappers import (to_customer_public, 
#                      to_customer_public_list,
#                      to_customer_with_orders_public,
# )

# from services.customers import (
#     create_customer_service, 
#     read_customer_service,
#     list_customers_service,
#     get_customer_with_orders_service
# )
                            

# from errors import (DuplicateCustomerEmailError, 
#                     CustomerNotFoundError,
#                     DataIntegrityError)

# router = APIRouter(prefix="/customers", tags=["customers"])




# @router.post("", response_model=CustomerPublic, status_code=201)
# def create_customer(
#     customer_create: CustomerCreate,
#     session: Session = Depends(get_session),
# ):
#     try:
#         db_customer = create_customer_service(
#             name=customer_create.name,
#             email=customer_create.email,
#             session=session,
#         )
#     except DuplicateCustomerEmailError as error:
#         raise HTTPException(
#             status_code=409,
#             detail=error.detail,
#         ) from error
    
#     except DataIntegrityError as error:
#         raise HTTPException(status_code=500, 
#                             detail='internal server error'
#                             ) from error
    
    
#     return to_customer_public(db_customer)


# @router.get("/{customer_id}", response_model=CustomerPublic)
# def read_customer(
#     customer_id: int,
#     session: Session = Depends(get_session),
# ):
    
#     try:
#         db_customer = read_customer_service(
#              customer_id=customer_id,
#              session=session)
        
#     except CustomerNotFoundError as error:
#          raise HTTPException(status_code=404, 
#                              detail=error.detail
#                              ) from error
    
#     return to_customer_public(db_customer)


# @router.get("", response_model=list[CustomerPublic])
# def list_customers(*,
#     name: Annotated[str | None, Query(min_length=1)] = None,
#     email: Annotated[str | None, Query(min_length=1)] = None,
#     sort_by: CustomerSortBy = 'name',
#     sort_dir: CustomerSortDirection = 'desc',
#     offset: Annotated[int, Query(ge = 0)] = 0,
#     limit: Annotated[int, Query(ge=0)] = 25,
#     session: Session = Depends(get_session)
# ):
#     db_customers = list_customers_service(
#           name=name,
#           email=email,
#           sort_by=sort_by,
#           sort_dir=sort_dir,
#           offset=offset,
#           limit=limit,
#           session=session
#      )

#     return to_customer_public_list(db_customers)



# @router.get(
#     "/{customer_id}/orders",
#     response_model=CustomerWithOrdersPublic,)
# def get_customer_with_orders(
#     customer_id: int,
#     session: Session = Depends(get_session),
# ) -> CustomerWithOrdersPublic:
#     try:
#         db_customer, db_orders = get_customer_with_orders_service(
#             customer_id=customer_id,
#             session=session,
#         )

#     except CustomerNotFoundError as error:
#         raise HTTPException(
#             status_code=404,
#             detail="customer not found",
#         ) from error

#     return to_customer_with_orders_public(
#         db_customer=db_customer,
#         db_orders=db_orders,
#     )