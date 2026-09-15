from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class SupplierBase(BaseModel):
    supplier_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)


class SupplierResponse(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
