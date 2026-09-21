import uuid
from datetime import datetime, timedelta

from app.ml.features import build_delivery_features
from app.ml.predict import predict_delivery_days


def predict_order_delivery(
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
    features = build_delivery_features(
        order_quantity=order_quantity,
        number_of_items=number_of_items,
        current_stock=current_stock,
        reorder_level=reorder_level,
        supplier_lead_time=supplier_lead_time,
        processing_time=processing_time,
        shipping_time=shipping_time,
    )

    prediction = predict_delivery_days(
        features
    )

    predicted_days = prediction[
        "predicted_fulfillment_days"
    ]

    predicted_delivery_date = (
        order_date
        + timedelta(days=predicted_days)
    )

    return {
        "order_id": order_id,
        "predicted_fulfillment_days": predicted_days,
        "predicted_delivery_date": predicted_delivery_date,
        "model_version": prediction[
            "model_version"
        ],
        "training_data_type": prediction[
            "training_data_type"
        ],
    }