from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr
from uuid import UUID
from ..models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: constr(min_length=1, max_length=100)
    role: Optional[UserRole] = Field(default=UserRole.USER)

class UserCreate(UserBase):
    password: constr(min_length=8, max_length=100)
    password_confirm: str

    def validate_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")

class UserUpdate(BaseModel):
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRole] = None

class UserInDB(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    """User model returned to the client (excludes sensitive data)"""
    pass

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    current_password: str
    new_password: constr(min_length=8, max_length=100)
    new_password_confirm: str

    def validate_passwords_match(self):
        if self.new_password != self.new_password_confirm:
            raise ValueError("New passwords do not match")
