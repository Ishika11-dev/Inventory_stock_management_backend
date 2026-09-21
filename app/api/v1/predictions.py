import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import prediction_controller
from app.core.database import get_db
from app.core.dependencies import require_super_admin_or_manager
from app.models.user import User
from app.schemas.prediction import DeliveryPredictionResponse

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/orders/{order_id}/delivery", response_model=DeliveryPredictionResponse)
def predict_order_delivery(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin_or_manager),
):
    return prediction_controller.predict_order_delivery(db, order_id)