import uuid
from datetime import datetime

from app.services import prediction_service


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
):
    return prediction_service.predict_order_delivery(
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