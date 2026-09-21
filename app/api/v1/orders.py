import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.controllers import order_controller
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db)
):
    return order_controller.create_order(
        db=db,
        data=data
    )


@router.get(
    "/",
    response_model=list[OrderResponse]
)
def get_orders(
    db: Session = Depends(get_db)
):
    return order_controller.list_orders(
        db=db
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    return order_controller.get_order(
        db=db,
        order_id=order_id
    )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse
)
def update_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    return order_controller.update_order_status(
        db=db,
        order_id=order_id,
        status=data.status
    )