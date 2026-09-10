from pydantic import BaseModel




#authenticated user + org they've been verified to access
class TenantContext(BaseModel):
    user_id: int
    organization_id: int

 