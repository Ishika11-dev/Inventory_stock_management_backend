from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)