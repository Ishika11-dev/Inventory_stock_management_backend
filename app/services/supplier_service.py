from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
)
from app.utils.exceptions import (
    ConflictException,
    NotFoundException,
)
import uuid

def create_supplier(
    db: Session,
    data: SupplierCreate
):
    supplier = Supplier(
        name=data.name,
        contact_email=str(data.contact_email),
        phone=data.phone,
        address=data.address
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


def get_suppliers(db: Session):
    return (
        db.query(Supplier)
        .filter(Supplier.is_deleted.is_(False))
        .all()
    )
def get_supplier(
    db: Session,
    supplier_id: uuid.UUID
):
    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id,
            Supplier.is_deleted.is_(False)
        )
        .first()
    )

    if not supplier:
        raise NotFoundException(
            "Supplier not found"
        )

    return supplier

def update_supplier(
    db: Session,
    supplier_id: uuid.UUID,
    data: SupplierUpdate
):
    supplier = db.get(
        Supplier,
        supplier_id
    )

    if not supplier:
        raise NotFoundException(
            "Supplier not found"
        )

    if data.name is not None:
        supplier.name = data.name

    if data.contact_email is not None:
        supplier.contact_email = str(
            data.contact_email
        )

    if data.phone is not None:
        supplier.phone = data.phone

    if data.address is not None:
        supplier.address = data.address

    db.commit()
    db.refresh(supplier)

    return supplier


def delete_supplier(
    db: Session,
    supplier_id: uuid.UUID
):
    supplier = db.get(
        Supplier,
        supplier_id
    )

    if not supplier:
        raise NotFoundException(
            "Supplier not found"
        )
    supplier.is_deleted = True
    db.commit()