from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.prediction import DeliveryPredictionResponse
from app.ml.synthetic_data import generate_synthetic_training_data
from app.utils.exceptions import NotFoundException

MODEL_VERSION = "synthetic-v1"
_model = None


def _get_model():
    global _model
    if _model is not None:
        return _model
    try:
        from xgboost import XGBRegressor
    except ImportError as error:
        raise RuntimeError("XGBoost is required for delivery prediction") from error

    rows, targets = generate_synthetic_training_data()
    _model = XGBRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=1,
    )
    _model.fit(rows, targets)
    return _model


def predict_order_delivery(db: Session, order_id):
    order = db.scalar(
        select(Order)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
            .selectinload(Product.supplier)
        )
        .where(Order.id == order_id)
    )
    if not order:
        raise NotFoundException("Order not found")

    quantities = sum(item.quantity for item in order.items)
    suppliers = [item.product.supplier for item in order.items if item.product and item.product.supplier]
    lead_time = max((supplier.lead_time_days for supplier in suppliers), default=7)
    delay = max((supplier.historical_delay_days for supplier in suppliers), default=0)
    reorder_level = sum(item.product.reorder_level for item in order.items)
    current_stock = sum(item.product.quantity_in_stock for item in order.items)
    features = [[
        quantities,
        len(order.items),
        float(order.total_amount),
        current_stock,
        order.shortage_quantity,
        reorder_level,
        lead_time,
        delay,
        2,
        3,
        order.created_at.weekday(),
        order.created_at.month,
    ]]
    predicted_days = max(1, round(float(_get_model().predict(features)[0])))
    delivery_date = datetime.now(timezone.utc) + timedelta(days=predicted_days)
    order.predicted_fulfillment_days = predicted_days
    order.predicted_delivery_date = delivery_date
    db.commit()
    db.refresh(order)
    return DeliveryPredictionResponse(
        order_id=order.id,
        predicted_fulfillment_days=predicted_days,
        predicted_delivery_date=delivery_date,
        training_source="synthetic training data; no historical completed orders were available",
        model_name="XGBoostRegressor",
        model_version=MODEL_VERSION,
    )
