from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services import user_service
from app.schemas.auth import UserRole


def change_user_role(
    db: Session,
    user_id,
    new_role: UserRole
):
    try:
        return user_service.change_user_role(
            db=db,
            user_id=user_id,
            new_role=new_role
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )