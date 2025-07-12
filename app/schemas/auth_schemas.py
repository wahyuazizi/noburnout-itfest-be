# app/schemas/auth_schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """Schema for user creation (signup)."""
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for the JWT token response."""
    access_token: str
    token_type: str = "bearer"
