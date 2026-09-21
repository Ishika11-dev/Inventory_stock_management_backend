from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_tracking import OrderTracking
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatus
from app.services.stock_service import record_movement
from app.utils.exceptions import BadRequestException, NotFoundException

ALLOWED_TRANSITIONS = {
    OrderStatus.AWAITING_STOCK.value: {OrderStatus.PROCESSING.value, OrderStatus.CANCELLED.value},
    OrderStatus.PROCESSING.value: {OrderStatus.PACKED.value, OrderStatus.CANCELLED.value},
    OrderStatus.PACKED.value: {OrderStatus.SHIPPED.value, OrderStatus.CANCELLED.value},
    OrderStatus.SHIPPED.value: {OrderStatus.OUT_FOR_DELIVERY.value},
    OrderStatus.OUT_FOR_DELIVERY.value: {OrderStatus.DELIVERED.value},
    OrderStatus.DELIVERED.value: set(),
    OrderStatus.CANCELLED.value: set(),
}


def _load_order(db: Session, order_id):
    order = db.scalar(
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.tracking))
        .where(Order.id == order_id)
    )
    if not order:
        raise NotFoundException("Order not found")
    return order


def _tracking(db: Session, order: Order, status: str, actor_id=None, note=None):
    db.add(OrderTracking(
        order_id=order.id,
        status=status,
        actor_id=actor_id,
        note=note,
        simulated=True,
    ))


def create_customer(db: Session, data):
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def create_order(db: Session, data: OrderCreate, actor_id=None):
    customer = db.get(Customer, data.customer_id)
    if not customer or not customer.is_active:
        raise NotFoundException("Customer not found")

    requested = {}
    for item in data.items:
        requested[item.product_id] = requested.get(item.product_id, 0) + item.quantity

    products = {}
    for product_id in sorted(requested, key=str):
        product = db.scalar(
            select(Product)
            .where(Product.id == product_id, Product.is_active.is_(True))
            .with_for_update()
        )
        if not product:
            raise NotFoundException(f"Product {product_id} not found")
        products[product_id] = product

    order = Order(customer_id=customer.id, status=OrderStatus.PROCESSING.value, total_amount=Decimal("0"))
    db.add(order)
    db.flush()

    shortage = 0
    for product_id, quantity in requested.items():
        product = products[product_id]
        reserved = min(product.quantity_in_stock, quantity)
        product.quantity_in_stock -= reserved
        if reserved:
            record_movement(db, product, "RESERVATION", reserved, "Customer order stock reservation", "ORDER", order.id, actor_id)
        shortage += quantity - reserved
        unit_price = Decimal(product.unit_price)
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            reserved_quantity=reserved,
            unit_price=unit_price,
            line_total=unit_price * quantity,
        ))
        order.total_amount += unit_price * quantity

    order.shortage_quantity = shortage
    order.status = OrderStatus.AWAITING_STOCK.value if shortage else OrderStatus.PROCESSING.value
    _tracking(db, order, order.status, actor_id, "Order created")
    db.commit()
    return _load_order(db, order.id)


def update_status(db: Session, order_id, status: str, actor_id=None, note=None):
    order = _load_order(db, order_id)
    if status == order.status:
        raise BadRequestException("Order is already in this status")
    if status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise BadRequestException(f"Cannot transition order from {order.status} to {status}")
    if status == OrderStatus.PROCESSING.value and order.shortage_quantity:
        raise BadRequestException("Order still has insufficient stock")
    if status == OrderStatus.CANCELLED.value:
        for item in order.items:
            if item.reserved_quantity:
                product = db.scalar(select(Product).where(Product.id == item.product_id).with_for_update())
                product.quantity_in_stock += item.reserved_quantity
                record_movement(db, product, "RELEASE", item.reserved_quantity, "Cancelled customer order", "ORDER", order.id, actor_id)
                item.reserved_quantity = 0
    order.status = status
    _tracking(db, order, status, actor_id, note)
    db.commit()
    return _load_order(db, order.id)
