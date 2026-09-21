import uuid

from sqlalchemy.orm import Session

from app.schemas.order import OrderCreate, OrderStatus
from app.services import order_service


def create_order(
    db: Session,
    data: OrderCreate
):
    return order_service.create_order(
        db=db,
        data=data
    )


def get_order(
    db: Session,
    order_id: uuid.UUID
):
    return order_service.get_order(
        db=db,
        order_id=order_id
    )


def list_orders(db: Session):
    return order_service.list_orders(db)


def update_order_status(
    db: Session,
    order_id: uuid.UUID,
    status: OrderStatus
):
    return order_service.update_order_status(
        db=db,
        order_id=order_id,
        new_status=status
    )