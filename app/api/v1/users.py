import uuid

from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin

from app.models.user import User

from app.schemas.auth import (
    UserResponse,
    UserRole
)

from app.schemas.user import RoleUpdateRequest

from app.controllers import user_controller


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse
)
def change_user_role(
    user_id: uuid.UUID,
    data: RoleUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return user_controller.change_user_role(
        db=db,
        user_id=user_id,
        new_role=data.role
    )