from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    description: str | None = None
    category: str | None = None
    unit: str
    reorder_level: float = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None
    category: str | None = None
    unit: str
    reorder_level: float = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None
    unit: str | None = None
    reorder_level: float | None = Field(default=None, ge=0)
    is_active: bool | None = None