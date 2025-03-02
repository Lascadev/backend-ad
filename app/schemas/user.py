from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    user: UserOut

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str