from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
import uuid



class UserRole(str, Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
    username: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)