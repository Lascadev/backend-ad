from pydantic import BaseModel
from app.schemas.user import UserOut

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
    refresh_token: str
    
    class Config:
        orm_mode = True