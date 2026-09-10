
from fastapi import (APIRouter, 
                     Depends,
                     HTTPException)

from sqlmodel import Session

from app.db import get_session
from app.services.users import create_user_service
from sqlmodel import SQLModel
from app.errors import DataIntegrityError
from typing import cast
from app.auth.context import AuthContext
from app.auth.dependencies import get_authenticated_user


# TEMPORARY / DEV-ONLY
class DevUserCreate(SQLModel):
    name: str
    email: str



router = APIRouter(prefix="/dev_onboarding", 
                   tags=["onboarding"])

@router.post("/users", 
             status_code=201)

def dev_create_user(
    user: DevUserCreate,
    session: Session = Depends(get_session),
):
    
    db_user = create_user_service(
        name=user.name,
        email=user.email,
        session=session,
    )

    return {
        "user_id": db_user.id,
    }



