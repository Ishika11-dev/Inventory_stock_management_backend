from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    AWAITING_STOCK = "AWAITING_STOCK"
    PROCESSING = "PROCESSING"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., min_length=3, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)


class CustomerResponse(CustomerCreate):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: uuid.UUID
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    reserved_quantity: int
    unit_price: Decimal
    line_total: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderTrackingResponse(BaseModel):
    id: uuid.UUID
    status: OrderStatus
    note: str | None
    actor_id: uuid.UUID | None
    simulated: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: OrderStatus
    total_amount: Decimal
    shortage_quantity: int
    predicted_fulfillment_days: int | None
    predicted_delivery_date: datetime | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]
    tracking: list[OrderTrackingResponse]
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    note: str | None = Field(default=None, max_length=500)
