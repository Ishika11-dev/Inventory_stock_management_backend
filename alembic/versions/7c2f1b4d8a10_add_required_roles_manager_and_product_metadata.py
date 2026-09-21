"""add required roles, manager ownership, and product metadata

Revision ID: 7c2f1b4d8a10
Revises: 5960cfc355e2
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c2f1b4d8a10"
down_revision: Union[str, Sequence[str], None] = "5960cfc355e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("manager_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        "ix_users_manager_id",
        "users",
        ["manager_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_users_manager_id_users",
        "users",
        "users",
        ["manager_id"],
        ["id"],
    )

    op.execute(
        "UPDATE users SET role = 'INVENTORY_MANAGER' "
        "WHERE role = 'ADMIN_MANAGER'"
    )
    op.execute(
        "UPDATE users SET role = 'ORDER_MANAGER' "
        "WHERE role = 'STAFF_MANAGER'"
    )
    op.execute(
        "UPDATE users SET role = 'INVENTORY_STAFF' "
        "WHERE role = 'ADMIN'"
    )
    op.execute(
        "UPDATE users SET role = 'ORDER_STAFF' "
        "WHERE role = 'STAFF'"
    )

    op.add_column("products", sa.Column("brand", sa.String(100)))
    op.add_column("products", sa.Column("model", sa.String(100)))
    op.add_column("products", sa.Column("description", sa.String(1000)))
    op.add_column("products", sa.Column("image_url", sa.String(500)))


def downgrade() -> None:
    op.drop_column("products", "image_url")
    op.drop_column("products", "description")
    op.drop_column("products", "model")
    op.drop_column("products", "brand")

    op.execute(
        "UPDATE users SET role = 'ADMIN_MANAGER' "
        "WHERE role = 'INVENTORY_MANAGER'"
    )
    op.execute(
        "UPDATE users SET role = 'STAFF_MANAGER' "
        "WHERE role = 'ORDER_MANAGER'"
    )
    op.execute(
        "UPDATE users SET role = 'ADMIN' "
        "WHERE role = 'INVENTORY_STAFF'"
    )
    op.execute(
        "UPDATE users SET role = 'STAFF' "
        "WHERE role = 'ORDER_STAFF'"
    )

    op.drop_constraint(
        "fk_users_manager_id_users",
        "users",
        type_="foreignkey",
    )
    op.drop_index("ix_users_manager_id", table_name="users")
    op.drop_column("users", "manager_id")