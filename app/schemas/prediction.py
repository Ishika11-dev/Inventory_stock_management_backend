from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class DeliveryPredictionResponse(BaseModel):
    order_id: uuid.UUID
    predicted_fulfillment_days: int
    predicted_delivery_date: datetime
    training_source: str
    model_name: str
    model_version: str
