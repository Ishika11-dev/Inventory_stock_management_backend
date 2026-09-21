import uuid
from datetime import datetime

from pydantic import BaseModel


class DeliveryPredictionResponse(BaseModel):
    order_id: uuid.UUID
    predicted_fulfillment_days: float
    predicted_delivery_date: datetime
    model_version: str
    training_data_type: str