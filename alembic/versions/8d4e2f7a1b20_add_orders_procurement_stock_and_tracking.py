"""add orders, procurement, stock movements, and tracking

Revision ID: 8d4e2f7a1b20
Revises: 7c2f1b4d8a10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d4e2f7a1b20"
down_revision: Union[str, Sequence[str], None] = "7c2f1b4d8a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def uuid_column(name, nullable=False, **kwargs):
    return sa.Column(name, sa.UUID(), nullable=nullable, **kwargs)


def upgrade() -> None:
    op.add_column(
        "suppliers",
        sa.Column("lead_time_days", sa.Integer(), nullable=False, server_default="7"),
    )
    op.add_column(
        "suppliers",
        sa.Column("historical_delay_days", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "customers",
        uuid_column("id", primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(30)),
        sa.Column("address", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_customers_id", "customers", ["id"])
    op.create_index("ix_customers_email", "customers", ["email"])

    op.create_table(
        "orders",
        uuid_column("id", primary_key=True),
        uuid_column("customer_id", nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="PROCESSING"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("shortage_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("predicted_fulfillment_days", sa.Integer()),
        sa.Column("predicted_delivery_date", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
    )
    op.create_index("ix_orders_id", "orders", ["id"])
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "order_items",
        uuid_column("id", primary_key=True),
        uuid_column("order_id", nullable=False),
        uuid_column("product_id", nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reserved_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
    )
    op.create_index("ix_order_items_id", "order_items", ["id"])
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"])

    op.create_table(
        "purchase_orders",
        uuid_column("id", primary_key=True),
        uuid_column("supplier_id", nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("expected_date", sa.DateTime()),
        sa.Column("received_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
    )
    op.create_index("ix_purchase_orders_id", "purchase_orders", ["id"])
    op.create_index("ix_purchase_orders_supplier_id", "purchase_orders", ["supplier_id"])
    op.create_index("ix_purchase_orders_status", "purchase_orders", ["status"])

    op.create_table(
        "purchase_order_items",
        uuid_column("id", primary_key=True),
        uuid_column("purchase_order_id", nullable=False),
        uuid_column("product_id", nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("received_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
    )
    op.create_index("ix_purchase_order_items_id", "purchase_order_items", ["id"])
    op.create_index("ix_purchase_order_items_purchase_order_id", "purchase_order_items", ["purchase_order_id"])
    op.create_index("ix_purchase_order_items_product_id", "purchase_order_items", ["product_id"])

    op.create_table(
        "stock_movements",
        uuid_column("id", primary_key=True),
        uuid_column("product_id", nullable=False),
        sa.Column("movement_type", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("reference_type", sa.String(30)),
        uuid_column("reference_id"),
        uuid_column("created_by_id"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
    )
    op.create_index("ix_stock_movements_id", "stock_movements", ["id"])
    op.create_index("ix_stock_movements_product_id", "stock_movements", ["product_id"])
    op.create_index("ix_stock_movements_reference_id", "stock_movements", ["reference_id"])

    op.create_table(
        "order_tracking",
        uuid_column("id", primary_key=True),
        uuid_column("order_id", nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("note", sa.String(500)),
        uuid_column("actor_id"),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
    )
    op.create_index("ix_order_tracking_id", "order_tracking", ["id"])
    op.create_index("ix_order_tracking_order_id", "order_tracking", ["order_id"])


def downgrade() -> None:
    op.drop_table("order_tracking")
    op.drop_table("stock_movements")
    op.drop_table("purchase_order_items")
    op.drop_table("purchase_orders")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_column("suppliers", "historical_delay_days")
    op.drop_column("suppliers", "lead_time_days")
