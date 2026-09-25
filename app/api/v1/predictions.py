import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.controllers import prediction_controller
from app.schemas.prediction import DeliveryPredictionResponse


router = APIRouter(
    prefix="/predictions",
    tags=["Delivery Prediction"],
)


@router.post(
    "/orders/{order_id}",
    response_model=DeliveryPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict delivery date for an existing order by ID (Auto-extracts DB features)"
)
def predict_order_delivery_by_id(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return prediction_controller.predict_by_order_id(
        db=db,
        order_id=order_id
    )


@router.post(
    "/delivery",
    response_model=DeliveryPredictionResponse,
)
def predict_delivery(
    order_id: uuid.UUID,
    order_date: datetime,
    order_quantity: int,
    number_of_items: int,
    current_stock: int,
    reorder_level: int,
    supplier_lead_time: int,
    processing_time: int,
    shipping_time: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return prediction_controller.predict_delivery(
        order_id=order_id,
        order_date=order_date,
        order_quantity=order_quantity,
        number_of_items=number_of_items,
        current_stock=current_stock,
        reorder_level=reorder_level,
        supplier_lead_time=supplier_lead_time,
        processing_time=processing_time,
        shipping_time=shipping_time,
    )