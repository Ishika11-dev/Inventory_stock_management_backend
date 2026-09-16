from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRole
from app.utils.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)


def get_users(db: Session):
    return (
        db.query(User)
        .order_by(User.username)
        .all()
    )


def get_team(
    db: Session,
    manager: User
):
    role = {
        UserRole.ADMIN_MANAGER.value: "ADMIN",
        UserRole.STAFF_MANAGER.value: "STAFF",
    }.get(manager.role)

    if not role:
        raise ForbiddenException(
            "No team for this role"
        )

    return (
        db.query(User)
        .filter(User.role == role)
        .order_by(User.username)
        .all()
    )


def update_role(
    db: Session,
    user_id,
    new_role: UserRole
):
    user = db.get(User, user_id)

    if not user:
        raise NotFoundException(
            "User not found"
        )

    # --------------------------------
    # Protect against losing the last
    # SUPER_ADMIN (prevents lockout)
    # --------------------------------

    if (
        user.role == UserRole.SUPER_ADMIN.value
        and new_role.value != UserRole.SUPER_ADMIN.value
    ):
        super_admin_count = db.scalar(
            select(func.count()).select_from(
                User
            ).where(
                User.role == UserRole.SUPER_ADMIN.value
            )
        )

        if super_admin_count <= 1:
            raise BadRequestException(
                "Cannot demote the last SUPER_ADMIN"
            )

    user.role = new_role.value

    db.commit()
    db.refresh(user)

    return user