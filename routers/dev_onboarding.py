
from fastapi import (APIRouter, 
                     Depends,)

from sqlmodel import Session

from db import get_session
from services.users import create_user_service
from sqlmodel import SQLModel


# TEMPORARY / DEV-ONLY
class DevUserCreate(SQLModel):
    name: str
    email: str


router = APIRouter(prefix="/dev_onboarding", 
                   tags=["onboarding"])

@router.post("/users")
def dev_create_user(
    user: DevUserCreate,
    session: Session = Depends(get_session),
):
    
    return create_user_service(
        name=user.name,
        email=user.email,
        session=session,
    )