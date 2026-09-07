from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
)

from app.services import supplier_service

from app.utils.exceptions import (
    ConflictException,
    NotFoundException,
)
import uuid

def create_supplier(
    db: Session,
    data: SupplierCreate
):
    try:
        return supplier_service.create_supplier(
            db,
            data
        )

    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


def get_suppliers(
    db: Session
):
    return supplier_service.get_suppliers(db)


def get_supplier(
    db: Session,
    supplier_id: uuid.UUID
):
    try:
        return supplier_service.get_supplier(
            db=db,
            supplier_id=supplier_id
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


def update_supplier(
    db: Session,
    supplier_id: uuid.UUID,
    data: SupplierUpdate
):
    try:
        return supplier_service.update_supplier(
            db,
            supplier_id,
            data
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


def delete_supplier(
    db: Session,
    supplier_id: uuid.UUID
):
    try:
        supplier_service.delete_supplier(
            db,
            supplier_id
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )