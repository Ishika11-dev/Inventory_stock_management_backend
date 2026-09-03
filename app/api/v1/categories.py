from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    require_admin,
    require_admin_or_staff,
)
from app.models.user import User

from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)

from app.controllers import category_controller


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return category_controller.create_category(
        db=db,
        data=data
    )


@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):
    return category_controller.get_categories(
        db=db
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):
    return category_controller.get_category(
        db=db,
        category_id=category_id
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return category_controller.update_category(
        db=db,
        category_id=category_id,
        data=data
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    category_controller.delete_category(
        db=db,
        category_id=category_id
    )