from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ProductionOrderStatus(str, Enum):
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    HALTED = "halted"


VALID_PROD_TRANSITIONS = {
    ProductionOrderStatus.PLANNED: [
        ProductionOrderStatus.SCHEDULED,
        ProductionOrderStatus.CANCELLED,
    ],
    ProductionOrderStatus.SCHEDULED: [
        ProductionOrderStatus.IN_PROGRESS,
        ProductionOrderStatus.CANCELLED,
    ],
    ProductionOrderStatus.IN_PROGRESS: [
        ProductionOrderStatus.COMPLETED,
        ProductionOrderStatus.HALTED,
        ProductionOrderStatus.CANCELLED,
    ],
    ProductionOrderStatus.HALTED: [
        ProductionOrderStatus.IN_PROGRESS,
        ProductionOrderStatus.CANCELLED,
    ],
    ProductionOrderStatus.COMPLETED: [],
    ProductionOrderStatus.CANCELLED: [],
}

VALID_PRODUCTION_TRANSITIONS = VALID_PROD_TRANSITIONS


class ProductionOrderBase(BaseModel):
    order_number: str = Field(..., max_length=50)
    product_id: UUID
    target_quantity: float = Field(..., gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    line_id: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class ProductionOrderCreate(ProductionOrderBase):
    pass


class ProductionOrderUpdate(BaseModel):
    target_quantity: Optional[float] = Field(None, gt=0)
    completed_quantity: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    line_id: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    status: Optional[ProductionOrderStatus] = None


class ProductionOrderResponse(ProductionOrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ProductionOrderStatus = ProductionOrderStatus.PLANNED
    completed_quantity: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
