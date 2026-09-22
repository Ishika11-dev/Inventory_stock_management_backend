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
    """
    Return only the staff members who are directly
    assigned to this manager.
    """

    # Only managers can view a team.
    if manager.role not in {
        UserRole.INVENTORY_MANAGER.value,
        UserRole.ORDER_MANAGER.value,
    }:
        raise ForbiddenException(
            "No team for this role"
        )

    return (
        db.query(User)
        .filter(
            User.manager_id == manager.id
        )
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
    # SUPER_ADMIN
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

    # --------------------------------
    # UPDATE ROLE
    # --------------------------------

    user.role = new_role.value

    # --------------------------------
    # CLEAR MANAGER WHEN USER IS NOT
    # A STAFF MEMBER
    # --------------------------------

    if new_role in {
        UserRole.SUPER_ADMIN,
        UserRole.INVENTORY_MANAGER,
        UserRole.ORDER_MANAGER,
    }:
        user.manager_id = None

    db.commit()
    db.refresh(user)

    return user