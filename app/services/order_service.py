import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatus


def create_order(
    db: Session,
    data: OrderCreate
):
    # ---------------------------------------------------------
    # 1. Check customer
    # ---------------------------------------------------------

    customer = (
        db.query(Customer)
        .filter(Customer.id == data.customer_id)
        .first()
    )

    if not customer:
        raise ValueError("Customer not found")

    # ---------------------------------------------------------
    # 2. Create order object
    # ---------------------------------------------------------

    order = Order(
        customer_id=customer.id,
        status=OrderStatus.ORDER_PLACED.value,
        total_amount=Decimal("0.00")
    )

    db.add(order)

    # Flush so order.id is generated before creating items
    db.flush()

    total_amount = Decimal("0.00")

    has_shortage = False

    # ---------------------------------------------------------
    # 3. Process each product
    # ---------------------------------------------------------

    for item_data in data.items:

        product = (
            db.query(Product)
            .filter(
                Product.product_id == item_data.product_id
            )
            .first()
        )

        if not product:
            raise ValueError(
                f"Product {item_data.product_id} not found"
            )

        # -----------------------------------------------------
        # 4. Check product availability
        # -----------------------------------------------------

        if not product.is_active:
            raise ValueError(
                f"Product '{product.name}' is inactive"
            )

        # -----------------------------------------------------
        # 5. Get current product price
        # -----------------------------------------------------

        unit_price = Decimal(str(product.unit_price))

        subtotal = unit_price * item_data.quantity

        total_amount += subtotal

        # -----------------------------------------------------
        # 6. Check stock
        # -----------------------------------------------------

        if product.quantity_in_stock < item_data.quantity:
            has_shortage = True

        # -----------------------------------------------------
        # 7. Create order item
        # -----------------------------------------------------

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.product_id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )

        db.add(order_item)

    # ---------------------------------------------------------
    # 8. Set order total
    # ---------------------------------------------------------

    order.total_amount = total_amount

    # ---------------------------------------------------------
    # 9. Determine initial status
    # ---------------------------------------------------------

    if has_shortage:
        order.status = OrderStatus.AWAITING_STOCK.value
    else:
        order.status = OrderStatus.CONFIRMED.value

    # ---------------------------------------------------------
    # 10. Save everything
    # ---------------------------------------------------------

    db.commit()
    db.refresh(order)

    # Load order items
    order.items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return order


def get_order(
    db: Session,
    order_id: uuid.UUID
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise ValueError("Order not found")

    order.items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return order


def list_orders(db: Session):
    orders = (
        db.query(Order)
        .order_by(Order.order_date.desc())
        .all()
    )

    for order in orders:
        order.items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

    return orders


def update_order_status(
    db: Session,
    order_id: uuid.UUID,
    new_status: OrderStatus
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise ValueError("Order not found")

    current_status = order.status

    # ---------------------------------------------------------
    # Allowed status transitions
    # ---------------------------------------------------------

    allowed_transitions = {
        "ORDER_PLACED": {
            "CONFIRMED",
            "CANCELLED"
        },

        "CONFIRMED": {
            "PROCESSING",
            "AWAITING_STOCK",
            "CANCELLED"
        },

        "PROCESSING": {
            "PACKED",
            "AWAITING_STOCK",
            "CANCELLED"
        },

        "AWAITING_STOCK": {
            "SUPPLIER_ORDER_PLACED",
            "CANCELLED"
        },

        "SUPPLIER_ORDER_PLACED": {
            "STOCK_RECEIVED",
            "CANCELLED"
        },

        "STOCK_RECEIVED": {
            "PROCESSING"
        },

        "PACKED": {
            "SHIPPED"
        },

        "SHIPPED": {
            "OUT_FOR_DELIVERY"
        },

        "OUT_FOR_DELIVERY": {
            "DELIVERED"
        },

        "DELIVERED": set(),

        "CANCELLED": set()
    }

    allowed = allowed_transitions.get(
        current_status,
        set()
    )

    if new_status.value not in allowed:
        raise ValueError(
            f"Cannot change order status "
            f"from {current_status} "
            f"to {new_status.value}"
        )

    order.status = new_status.value

    db.commit()
    db.refresh(order)

    order.items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return order