import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.utils.exceptions import NotFoundException, BadRequestException
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


def predict_by_order_id(db: Session, order_id: uuid.UUID):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise NotFoundException(f"Order with ID {order_id} not found")

    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    if not items:
        raise BadRequestException(f"Order {order_id} has no line items to predict delivery for")

    total_quantity = sum(item.quantity for item in items)
    number_of_items = len(items)

    product_ids = [item.product_id for item in items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()

    if products:
        current_stock = sum(p.quantity_in_stock for p in products)
        reorder_level = max(p.reorder_level for p in products)
    else:
        current_stock = 0
        reorder_level = 10

    # Logistics calculations: if warehouse stock has a deficit, supplier reorder lead time is needed
    has_deficit = current_stock < total_quantity
    supplier_lead_time = 4 if has_deficit else 2
    processing_time = 1
    shipping_time = 3

    result = predict_order_delivery(
        order_id=order.id,
        order_date=order.order_date,
        order_quantity=total_quantity,
        number_of_items=number_of_items,
        current_stock=current_stock,
        reorder_level=reorder_level,
        supplier_lead_time=supplier_lead_time,
        processing_time=processing_time,
        shipping_time=shipping_time,
    )

    # Automatically save predicted delivery date on the order in database!
    order.predicted_delivery_date = result["predicted_delivery_date"]
    db.commit()
    db.refresh(order)

    return result