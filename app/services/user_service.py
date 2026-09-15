from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRole


def change_user_role(
    db: Session,
    user_id,
    new_role: UserRole
):
    # -----------------------------------------
    # Find target user
    # -----------------------------------------
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    # -----------------------------------------
    # Nothing to change
    # -----------------------------------------
    if user.role == new_role:
        return user

    # -----------------------------------------
    # Prevent removing the last ADMIN
    # -----------------------------------------
    if (
        user.role == UserRole.ADMIN
        and new_role == UserRole.STAFF
    ):

        admin_count = (
            db.query(User)
            .filter(User.role == UserRole.ADMIN)
            .count()
        )

        if admin_count == 1:
            raise ValueError(
                "Cannot remove the last admin"
            )

    # -----------------------------------------
    # Change role
    # -----------------------------------------
    user.role = new_role

    db.commit()
    db.refresh(user)

    return user