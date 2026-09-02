from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.core.dependencies import (
    require_admin,
    require_admin_or_staff
)

from app.models.user import User

from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate
)

from app.services import category_service

from app.utils.exceptions import (
    ConflictException,
    NotFoundException
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# ==========================================
# CREATE CATEGORY
# ADMIN ONLY
# ==========================================

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

    try:

        return category_service.create_category(
            db,
            data
        )

    except ConflictException as e:

        raise HTTPException(
            status_code=409,
            detail=e.message
        )


# ==========================================
# GET CATEGORIES
# ADMIN + STAFF
# ==========================================

@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):

    return category_service.get_categories(db)


# ==========================================
# UPDATE CATEGORY
# ADMIN ONLY
# ==========================================

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

    try:

        return category_service.update_category(
            db,
            category_id,
            data
        )

    except NotFoundException as e:

        raise HTTPException(
            status_code=404,
            detail=e.message
        )

    except ConflictException as e:

        raise HTTPException(
            status_code=409,
            detail=e.message
        )


# ==========================================
# DELETE CATEGORY
# ADMIN ONLY
# ==========================================

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    try:

        category_service.delete_category(
            db,
            category_id
        )

    except NotFoundException as e:

        raise HTTPException(
            status_code=404,
            detail=e.message
        )

    except ConflictException as e:

        raise HTTPException(
            status_code=409,
            detail=e.message
        )