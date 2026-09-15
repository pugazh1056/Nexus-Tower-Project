from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class PurchaseOrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


VALID_PO_TRANSITIONS = {
    PurchaseOrderStatus.DRAFT: [
        PurchaseOrderStatus.PENDING_APPROVAL,
        PurchaseOrderStatus.CANCELLED,
    ],
    PurchaseOrderStatus.PENDING_APPROVAL: [
        PurchaseOrderStatus.APPROVED,
        PurchaseOrderStatus.CANCELLED,
    ],
    PurchaseOrderStatus.APPROVED: [
        PurchaseOrderStatus.ORDERED,
        PurchaseOrderStatus.CANCELLED,
    ],
    PurchaseOrderStatus.ORDERED: [
        PurchaseOrderStatus.PARTIALLY_RECEIVED,
        PurchaseOrderStatus.RECEIVED,
        PurchaseOrderStatus.CANCELLED,
    ],
    PurchaseOrderStatus.PARTIALLY_RECEIVED: [
        PurchaseOrderStatus.RECEIVED,
        PurchaseOrderStatus.CANCELLED,
    ],
    PurchaseOrderStatus.RECEIVED: [],
    PurchaseOrderStatus.CANCELLED: [],
}


class PurchaseOrderItemBase(BaseModel):
    product_id: UUID
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    received_quantity: float = Field(default=0.0, ge=0)


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    received_quantity: Optional[float] = Field(None, ge=0)


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    po_id: Optional[UUID] = None
    line_total: float = 0.0


class PurchaseOrderBase(BaseModel):
    po_number: str = Field(..., max_length=50)
    supplier_id: UUID
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate] = []


class PurchaseOrderUpdate(BaseModel):
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[PurchaseOrderStatus] = None
    items: Optional[List[PurchaseOrderItemCreate]] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    total_amount: float = 0.0
    items: List[PurchaseOrderItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
