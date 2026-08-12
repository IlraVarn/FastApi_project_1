#AUTHENTICATION BOUNDARY


import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


class AuthContext(BaseModel):
    user_id: int


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AuthContext:
    
    """Authenticate the request and return trusted internal identity."""

    expected_token = os.environ.get("DEV_AUTH_TOKEN")

    if expected_token is None:
        raise RuntimeError("DEV_AUTH_TOKEN is not configured")

    if not secrets.compare_digest(
        credentials.credentials,
        expected_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthContext(user_id=1)


