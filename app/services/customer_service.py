import uuid

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(
    db: Session,
    data: CustomerCreate
):
    customer = Customer(
        name=data.name,
        email=str(data.email).lower(),
        phone=data.phone,
        address=data.address,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_customer(
    db: Session,
    customer_id: uuid.UUID
):
    return (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )


def list_customers(db: Session):
    return db.query(Customer).order_by(Customer.created_at.desc()).all()


def update_customer(
    db: Session,
    customer: Customer,
    data: CustomerUpdate
):
    values = data.model_dump(exclude_unset=True)

    if "email" in values and values["email"]:
        values["email"] = str(values["email"]).lower()

    for key, value in values.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer