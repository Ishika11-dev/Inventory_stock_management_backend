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
    confirm_password: str,
    role: UserRole
):
    try:
        user = register_user(
            db=db,
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            role=role
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def login(
    db: Session,
    email: str,
    password: str
):
    token = login_user(
        db=db,
        email=email,
        password=password
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }