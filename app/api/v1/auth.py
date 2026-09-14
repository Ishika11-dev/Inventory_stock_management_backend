from fastapi import APIRouter, Depends, security, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    AccessTokenResponse
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
    data: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security), #holds the credentials sent in the HTTP Authorization header.
    db: Session = Depends(get_db)
):
    token = credentials.credentials #store bearer's token in the variable token.

    return auth_controller.logout(
        db=db,
        access_token=token,
        refresh_token=data.refresh_token 
    )

@router.post(
    "/refresh",
    response_model=AccessTokenResponse
)
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):

    return auth_controller.refresh_token(
        db=db,
        refresh_token=data.refresh_token
    )