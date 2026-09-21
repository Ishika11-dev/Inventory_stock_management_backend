import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers import procurement_controller
from app.core.database import get_db
from app.core.dependencies import require_super_admin_or_manager
from app.models.user import User
from app.schemas.procurement import PurchaseOrderCreate, PurchaseOrderResponse, PurchaseReceipt

router = APIRouter(prefix="/procurement", tags=["Procurement"])


@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(data: PurchaseOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin_or_manager)):
    return procurement_controller.create_purchase_order(db, data)


@router.post("/purchase-orders/{purchase_order_id}/receive", response_model=PurchaseOrderResponse)
def receive_purchase_order(purchase_order_id: uuid.UUID, data: PurchaseReceipt, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin_or_manager)):
    return procurement_controller.receive_purchase_order(db, purchase_order_id, data, current_user.id)
