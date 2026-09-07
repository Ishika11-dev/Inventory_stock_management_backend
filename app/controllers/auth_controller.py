from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import UserRole
from app.services.auth_service import (
    register_user,
    login_user,
)


def register(
    db: Session,
    username: str,
    email: str,
    password: str,
    role : UserRole
):
    user = register_user(
        db=db,
        username=username,
        email=email,
        password=password,
        role=role
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    return user


def login(
    db: Session,
    username: str,
    password: str
):
    token = login_user(
        db=db,
        username=username,
        password=password
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }