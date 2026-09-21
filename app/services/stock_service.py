from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.utils.exceptions import BadRequestException, NotFoundException


def lock_product(db: Session, product_id):
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id, Product.is_active.is_(True))
        .with_for_update()
    )
    if not product:
        raise NotFoundException("Product not found")
    return product


def record_movement(
    db: Session,
    product: Product,
    movement_type: str,
    quantity: int,
    reason: str,
    reference_type: str | None = None,
    reference_id=None,
    created_by_id=None,
):
    if quantity <= 0:
        raise BadRequestException("Stock movement quantity must be positive")
    db.add(StockMovement(
        product_id=product.id,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
        reference_type=reference_type,
        reference_id=reference_id,
        created_by_id=created_by_id,
    ))


def adjust_stock(db: Session, product_id, quantity: int, operation: str, reason: str, actor_id=None):
    product = lock_product(db, product_id)
    if operation == "IN":
        product.quantity_in_stock += quantity
        movement_type = "ADJUSTMENT_IN"
    else:
        if product.quantity_in_stock < quantity:
            raise BadRequestException("Insufficient stock for this adjustment")
        product.quantity_in_stock -= quantity
        movement_type = "ADJUSTMENT_OUT"
    record_movement(db, product, movement_type, quantity, reason, created_by_id=actor_id)
    db.commit()
    db.refresh(product)
    return product
