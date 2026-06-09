from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import desc


from db import get_session
from models import CustomerPublic, Customer, CustomerCreate
from mappers import to_customer_public
from services.customers import (
    create_customer_service, 
    read_customer_service
)
                            
from errors import NotFoundError, ConflictError

router = APIRouter(prefix="/customers", tags=["customers"])



@router.post("", response_model=CustomerPublic)
def create_customer(
    customer: CustomerCreate, 
    session: Session = Depends(get_session)):

        try:
             db_customer = create_customer_service(
                 customer_create=customer, 
                 session = session,)
             
        except ConflictError as error:
            raise HTTPException(status_code=409, detail=error.detail)

        return to_customer_public(db_customer)


@router.get("/{customer_id}", response_model=CustomerPublic)
def read_customer(
    customer_id: int,
    session: Session = Depends(get_session),
):
    
    try:
        db_customer = read_customer_service(
             customer_id=customer_id,
             session=session)
        
    except NotFoundError as error:
         raise HTTPException(status_code=404, detail=error.detail)
    
    return to_customer_public(db_customer)

