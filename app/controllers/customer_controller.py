import uuid

from sqlalchemy.orm import Session

from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services import customer_service


def create_customer(
    db: Session,
    data: CustomerCreate
):
    return customer_service.create_customer(db, data)


def get_customer(
    db: Session,
    customer_id: uuid.UUID
):
    customer = customer_service.get_customer(db, customer_id)

    if not customer:
        raise ValueError("Customer not found")

    return customer


def list_customers(db: Session):
    return customer_service.list_customers(db)


def update_customer(
    db: Session,
    customer_id: uuid.UUID,
    data: CustomerUpdate
):
    customer = customer_service.get_customer(db, customer_id)

    if not customer:
        raise ValueError("Customer not found")

    return customer_service.update_customer(
        db,
        customer,
        data
    )