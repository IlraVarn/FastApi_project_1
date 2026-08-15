#AUTHENTICATION BOUNDARY


import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

#basemodel object that contains only trusted id info needed downstream
class AuthContext(BaseModel):
    user_id: int

#parses http header schema and credentials
bearer_scheme = HTTPBearer()


#verifies user creditials, returns an AuthContext object
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
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

    return AuthContext(user_id=1)


