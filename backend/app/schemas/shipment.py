from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ShipmentStatus(str, Enum):
    PREPARING = "preparing"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


VALID_SHIPMENT_TRANSITIONS = {
    ShipmentStatus.PREPARING: [
        ShipmentStatus.DISPATCHED,
        ShipmentStatus.CANCELLED,
    ],
    ShipmentStatus.DISPATCHED: [
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.DELAYED,
        ShipmentStatus.CANCELLED,
    ],
    ShipmentStatus.IN_TRANSIT: [
        ShipmentStatus.DELAYED,
        ShipmentStatus.DELIVERED,
        ShipmentStatus.CANCELLED,
    ],
    ShipmentStatus.DELAYED: [
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.DELIVERED,
        ShipmentStatus.CANCELLED,
    ],
    ShipmentStatus.DELIVERED: [],
    ShipmentStatus.CANCELLED: [],
}


class ShipmentBase(BaseModel):
    tracking_number: str = Field(..., max_length=100)
    carrier: str = Field(..., max_length=100)
    origin: str = Field(..., max_length=255)
    destination: str = Field(..., max_length=255)
    po_id: Optional[UUID] = None
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    notes: Optional[str] = None


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    carrier: Optional[str] = Field(None, max_length=100)
    origin: Optional[str] = Field(None, max_length=255)
    destination: Optional[str] = Field(None, max_length=255)
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[ShipmentStatus] = None


class ShipmentResponse(ShipmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ShipmentStatus = ShipmentStatus.PREPARING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
