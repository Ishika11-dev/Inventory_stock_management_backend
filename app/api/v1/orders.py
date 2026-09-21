import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers import order_controller
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.order import CustomerCreate, CustomerResponse, OrderCreate, OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return order_controller.create_customer(db, data)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return order_controller.create_order(db, data, current_user.id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: uuid.UUID, data: OrderStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return order_controller.update_status(db, order_id, data, current_user.id)
