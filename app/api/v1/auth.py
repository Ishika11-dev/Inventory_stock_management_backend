from fastapi import APIRouter, Depends, security, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
   
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

from app.controllers import auth_controller


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    return auth_controller.register(
        db=db,
        username=data.username,
        email=data.email,
        password=data.password,
        confirm_password=data.confirm_password,
        role=data.role
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    return auth_controller.login(
        db=db,
        email=data.email,
        password=data.password
    )
@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    return auth_controller.logout(
        db,
        token
    )