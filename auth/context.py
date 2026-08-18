from pydantic import BaseModel


#who authenticated?
class AuthContext(BaseModel):
    user_id: int

