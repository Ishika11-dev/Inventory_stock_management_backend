from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.dependencies import (
    require_admin,
    require_admin_or_staff
)

from app.models.user import User

from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)

from app.services import supplier_service

from app.utils.exceptions import (
    ConflictException,
    NotFoundException,
)


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


# ==========================================
# CREATE SUPPLIER
# ADMIN ONLY
# ==========================================

@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED
)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    try:

        return supplier_service.create_supplier(
            db,
            data
        )

    except ConflictException as e:

        raise HTTPException(
            status_code=409,
            detail=e.message
        )


# ==========================================
# GET SUPPLIERS
# ADMIN + STAFF
# ==========================================

@router.get(
    "/",
    response_model=list[SupplierResponse]
)
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):

    return supplier_service.get_suppliers(db)


# ==========================================
# UPDATE SUPPLIER
# ADMIN ONLY
# ==========================================

@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    try:

        return supplier_service.update_supplier(
            db,
            supplier_id,
            data
        )

    except NotFoundException as e:

        raise HTTPException(
            status_code=404,
            detail=e.message
        )


# ==========================================
# DELETE SUPPLIER
# ADMIN ONLY
# ==========================================

@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    try:

        supplier_service.delete_supplier(
            db,
            supplier_id
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