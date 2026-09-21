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
        UserRole.INVENTORY_MANAGER.value: UserRole.INVENTORY_STAFF.value,
        UserRole.ORDER_MANAGER.value: UserRole.ORDER_STAFF.value,
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
    new_role: UserRole,
    manager_id=None,
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

    manager_roles = {
        UserRole.INVENTORY_MANAGER.value,
        UserRole.ORDER_MANAGER.value,
    }
    staff_roles = {
        UserRole.INVENTORY_STAFF.value,
        UserRole.ORDER_STAFF.value,
    }

    manager = None
    if new_role.value in staff_roles:
        if manager_id is None:
            raise BadRequestException(
                "Staff users must belong to a manager"
            )

        manager = db.get(User, manager_id)
        if not manager or manager.role not in manager_roles:
            raise BadRequestException(
                "manager_id must reference a matching manager"
            )

        expected_staff_role = (
            UserRole.INVENTORY_STAFF.value
            if manager.role == UserRole.INVENTORY_MANAGER.value
            else UserRole.ORDER_STAFF.value
        )
        if new_role.value != expected_staff_role:
            raise BadRequestException(
                "Staff role does not match the manager team"
            )
    elif manager_id is not None:
        raise BadRequestException(
            "Only staff users can have a manager_id"
        )

    user.role = new_role.value
    user.manager_id = manager.id if manager else None

    db.commit()
    db.refresh(user)

    return user