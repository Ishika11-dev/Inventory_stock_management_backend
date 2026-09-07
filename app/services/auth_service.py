import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRole

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
import uuid

def register_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: UserRole
):
    email = email.lower()

    # --------------------------------
    # CHECK EMAIL + ROLE
    # --------------------------------

    if role == UserRole.ADMIN:

        if not email.endswith("@admin.com"):
            raise ValueError(
                "ADMIN users must use an @admin.com email"
            )

    elif role == UserRole.STAFF:

        if not email.endswith("@staff.com"):
            raise ValueError(
                "STAFF users must use an @staff.com email"
            )

    # --------------------------------
    # CHECK USERNAME
    # --------------------------------

    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user:
        raise ValueError(
            "Username already exists"
        )

    # --------------------------------
    # CHECK EMAIL
    # --------------------------------

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        raise ValueError(
            "Email already exists"
        )

    # --------------------------------
    # HASH PASSWORD
    # --------------------------------

    hashed_password = hash_password(password)

    # --------------------------------
    # CREATE USER
    # --------------------------------

    user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role=role.value
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    username: str,
    password: str
):

    # --------------------------------
    # FIND USER
    # --------------------------------

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        return None

    # --------------------------------
    # VERIFY PASSWORD
    # --------------------------------

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user


def login_user(
    db: Session,
    username: str,
    password: str
):

    user = authenticate_user(
        db,
        username,
        password
    )

    if not user:
        return None

    # --------------------------------
    # CREATE JWT
    # --------------------------------

    token = create_access_token(
        {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role
        }
    )

    return token