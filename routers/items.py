from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy import desc
from datetime import datetime, UTC
from mappers import to_item_public
from errors import NotFoundError, ConflictError

from db import get_session
from models import (OrderItemPublic, OrderItemCreate)
from mappers import to_item_public
from typing import Annotated
from services.items import create_item_service

router = APIRouter(prefix="/items", tags=["items"])

@router.post("", response_model=OrderItemPublic)
def create_item(item: OrderItemCreate, session: Session = Depends(get_session)):

    try:
        db_item = create_item_service(
            item=item, 
            session=session
            )

    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail)
    
    return(to_item_public(db_item))




   

