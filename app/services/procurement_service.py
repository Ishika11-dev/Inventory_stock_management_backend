from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_tracking import OrderTracking
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier
from app.schemas.procurement import PurchaseOrderCreate, PurchaseReceipt
from app.services.stock_service import record_movement
from app.utils.exceptions import BadRequestException, ConflictException, NotFoundException


def _load_purchase_order(db: Session, purchase_order_id):
    purchase_order = db.scalar(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .where(PurchaseOrder.id == purchase_order_id)
    )
    if not purchase_order:
        raise NotFoundException("Purchase order not found")
    return purchase_order


def create_purchase_order(db: Session, data: PurchaseOrderCreate):
    supplier = db.get(Supplier, data.supplier_id)
    if not supplier or supplier.is_deleted:
        raise NotFoundException("Supplier not found")

    product_ids = [item.product_id for item in data.items]
    products = db.scalars(select(Product).where(Product.id.in_(product_ids), Product.is_active.is_(True))).all()
    product_map = {product.id: product for product in products}
    if len(product_map) != len(set(product_ids)):
        raise NotFoundException("One or more products were not found")
    if any(product.supplier_id != supplier.id for product in products):
        raise BadRequestException("All purchase-order products must belong to the selected supplier")

    for item in data.items:
        open_order = db.scalar(
            select(PurchaseOrderItem)
            .join(PurchaseOrder)
            .where(
                PurchaseOrderItem.product_id == item.product_id,
                PurchaseOrder.supplier_id == supplier.id,
                PurchaseOrder.status.in_(["DRAFT", "ORDERED", "PARTIALLY_RECEIVED"]),
            )
        )
        if open_order:
            raise ConflictException("An open purchase order already covers this product")

    purchase_order = PurchaseOrder(
        supplier_id=supplier.id,
        status="ORDERED",
        expected_date=data.expected_date,
        total_amount=sum((item.unit_price * item.quantity for item in data.items), Decimal("0")),
    )
    db.add(purchase_order)
    db.flush()
    for item in data.items:
        db.add(PurchaseOrderItem(
            purchase_order_id=purchase_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        ))
    db.commit()
    return _load_purchase_order(db, purchase_order.id)


def receive_purchase_order(db: Session, purchase_order_id, data: PurchaseReceipt, actor_id=None):
    purchase_order = _load_purchase_order(db, purchase_order_id)
    if purchase_order.status in {"RECEIVED", "CANCELLED"}:
        raise BadRequestException("Purchase order cannot receive stock in its current status")
    item_map = {item.id: item for item in purchase_order.items}
    if any(receipt.item_id not in item_map for receipt in data.items):
        raise NotFoundException("Purchase-order item not found")

    for receipt in data.items:
        item = item_map[receipt.item_id]
        available = item.quantity - item.received_quantity
        if receipt.quantity > available:
            raise BadRequestException("Receipt exceeds the ordered quantity")
        product = db.scalar(select(Product).where(Product.id == item.product_id).with_for_update())
        product.quantity_in_stock += receipt.quantity
        item.received_quantity += receipt.quantity
        record_movement(db, product, "RECEIPT", receipt.quantity, "Purchase order receipt", "PURCHASE_ORDER", purchase_order.id, actor_id)

        remaining = receipt.quantity
        waiting_items = db.scalars(
            select(OrderItem)
            .join(Order)
            .where(
                OrderItem.product_id == product.id,
                Order.status == "AWAITING_STOCK",
                OrderItem.reserved_quantity < OrderItem.quantity,
            )
            .order_by(Order.created_at)
            .with_for_update()
        ).all()
        for order_item in waiting_items:
            if remaining == 0:
                break
            allocation = min(
                remaining,
                order_item.quantity - order_item.reserved_quantity,
                product.quantity_in_stock,
            )
            if allocation <= 0:
                break
            product.quantity_in_stock -= allocation
            order_item.reserved_quantity += allocation
            order_item.order.shortage_quantity -= allocation
            remaining -= allocation
            record_movement(
                db,
                product,
                "RESERVATION",
                allocation,
                "Received stock allocated to waiting order",
                "ORDER",
                order_item.order_id,
                actor_id,
            )
            if order_item.order.shortage_quantity == 0:
                order_item.order.status = "PROCESSING"
                db.add(OrderTracking(
                    order_id=order_item.order_id,
                    status="PROCESSING",
                    note="Required stock received and reserved",
                    actor_id=actor_id,
                    simulated=True,
                ))

    purchase_order.status = "RECEIVED" if all(item.received_quantity == item.quantity for item in purchase_order.items) else "PARTIALLY_RECEIVED"
    if purchase_order.status == "RECEIVED":
        purchase_order.received_at = datetime.now(timezone.utc)
    db.commit()
    return _load_purchase_order(db, purchase_order.id)
