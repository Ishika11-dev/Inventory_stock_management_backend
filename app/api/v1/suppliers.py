from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    require_admin,
    require_admin_or_staff,
)
from app.models.user import User

from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)

from app.controllers import supplier_controller


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


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
    return supplier_controller.create_supplier(
        db=db,
        data=data
    )


@router.get(
    "/",
    response_model=list[SupplierResponse]
)
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):
    return supplier_controller.get_suppliers(
        db=db
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):
    return supplier_controller.get_supplier(
        db=db,
        supplier_id=supplier_id
    )


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
    return supplier_controller.update_supplier(
        db=db,
        supplier_id=supplier_id,
        data=data
    )


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    supplier_controller.delete_supplier(
        db=db,
        supplier_id=supplier_id
    )