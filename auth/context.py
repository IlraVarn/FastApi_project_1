from pydantic import BaseModel


#who authenticated?
class AuthContext(BaseModel):
    user_id: int

#authenticated user + org they've been verified to access
class TenantContext(BaseModel):
    user_id: int
    organization_id: int

