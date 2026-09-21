from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid

from pydantic import BaseModel, ConfigDict, Field


class PurchaseOrderStatus(str, Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class PurchaseOrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)


class PurchaseOrderCreate(BaseModel):
    supplier_id: uuid.UUID
    items: list[PurchaseOrderItemCreate] = Field(..., min_length=1)
    expected_date: datetime | None = None


class PurchaseReceiptItem(BaseModel):
    item_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class PurchaseReceipt(BaseModel):
    items: list[PurchaseReceiptItem] = Field(..., min_length=1)


class PurchaseOrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    received_quantity: int
    unit_price: Decimal
    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderResponse(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    status: PurchaseOrderStatus
    total_amount: Decimal
    expected_date: datetime | None
    received_at: datetime | None
    created_at: datetime
    items: list[PurchaseOrderItemResponse]
    model_config = ConfigDict(from_attributes=True)
