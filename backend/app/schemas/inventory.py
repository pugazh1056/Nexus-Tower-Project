from uuid import UUID
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class InventoryBase(BaseModel):
    product_id: UUID
    location_id: Optional[UUID] = None
    warehouse_name: Optional[str] = Field(None, max_length=100)
    warehouse_location: Optional[str] = None
    location: Optional[str] = None
    quantity_available: Optional[float] = Field(default=0.0, ge=0)
    quantity_reserved: Optional[float] = Field(default=0.0, ge=0)
    quantity: Optional[float] = Field(default=None, ge=0)
    quantity_on_hand: Optional[float] = Field(default=None, ge=0)
    reserved_quantity: Optional[float] = Field(default=None, ge=0)
    available_quantity: Optional[float] = Field(default=None)
    reorder_level: Optional[float] = Field(default=0.0, ge=0)
    reorder_threshold: Optional[float] = Field(default=None, ge=0)
    unit: Optional[str] = None
    status: Optional[str] = None
    batch_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[datetime] = None
    expiration_date: Optional[str] = None
    last_updated: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Location normalization
            loc = data.get("location") or data.get("warehouse_location") or data.get("warehouse_name")
            if loc:
                data.setdefault("location", loc)
                data.setdefault("warehouse_name", loc)
                data.setdefault("warehouse_location", loc)
            
            # Quantity normalization
            qty = data.get("quantity_available") or data.get("available_quantity") or data.get("quantity_on_hand") or data.get("quantity") or 0.0
            data.setdefault("quantity_available", float(qty))
            
            # Reserved quantity
            res_qty = data.get("quantity_reserved") or data.get("reserved_quantity") or 0.0
            data.setdefault("quantity_reserved", float(res_qty))
            
            # Reorder threshold
            reorder = data.get("reorder_threshold") or data.get("reorder_level") or 0.0
            data.setdefault("reorder_level", float(reorder))
        return data


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity_available: Optional[float] = Field(None, ge=0)
    quantity_reserved: Optional[float] = Field(None, ge=0)
    quantity: Optional[float] = Field(None, ge=0)
    quantity_on_hand: Optional[float] = Field(None, ge=0)
    reserved_quantity: Optional[float] = Field(None, ge=0)
    warehouse_location: Optional[str] = None
    location: Optional[str] = None
    reorder_level: Optional[float] = Field(None, ge=0)
    reorder_threshold: Optional[float] = Field(None, ge=0)
    batch_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[datetime] = None
    expiration_date: Optional[str] = None
    status: Optional[str] = None


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
