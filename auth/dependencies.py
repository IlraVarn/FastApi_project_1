#AUTHENTICATION BOUNDARY
import os
import secrets
from typing import Annotated
from sqlmodel import Session
from services.tenancy import resolve_tenant_context_service
from errors import TenantAccessDeniedError
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth.context import AuthContext
from tenancy.context import TenantContext
from db import get_session
from sqlmodel import Session
from models import User

#security scheme
#parses Authorization header and extracts Bearer credentials
bearer_scheme = HTTPBearer()


# TEMPORARY / DEV-ONLY
# verifies the DEV bearer token and returns the hardcoded DEV identity
def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session)
) -> AuthContext:
    
    """Authenticate the request and return trusted internal identity."""

    #gets the environmental variable from terminal in our example
    expected_token = os.environ.get("DEV_AUTH_TOKEN")

    if expected_token is None:
        raise RuntimeError("DEV_AUTH_TOKEN is not configured")

    #securely compares credentials to token
    if not secrets.compare_digest(
        credentials.credentials,
        expected_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    
    dev_user_id = int(os.environ["DEV_AUTH_USER_ID"])

    db_user = session.get(User, dev_user_id)

    if db_user is None or db_user.archived_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    if db_user.id is None:
        raise RuntimeError("Persisted user has no id")

    return AuthContext(
        user_id=db_user.id,
    )


"""Exact execution trace:
    Client sends HTTP request
    Authorization: Bearer abc123
            ↓
    HTTPBearer()
            ↓
    extracts "abc123"
            ↓
    credentials.credentials
            ↓
    get_current_user()
            ↓
    reads DEV_AUTH_TOKEN from environment
            ↓
    secure comparison
            ↓
    match
            ↓
    AuthContext(user_id=1)"""


