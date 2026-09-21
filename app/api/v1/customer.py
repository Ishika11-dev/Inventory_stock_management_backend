import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.controllers import customer_controller
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db)
):
    return customer_controller.create_customer(
        db=db,
        data=data
    )


@router.get(
    "/",
    response_model=list[CustomerResponse]
)
def get_customers(
    db: Session = Depends(get_db)
):
    return customer_controller.list_customers(db)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    return customer_controller.get_customer(
        db=db,
        customer_id=customer_id
    )


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse
)
def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    return customer_controller.update_customer(
        db=db,
        customer_id=customer_id,
        data=data
    )