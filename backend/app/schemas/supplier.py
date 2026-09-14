"""Supplier request and response models."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr

SupplierStatus = Literal["active"]


class SupplierCreate(BaseModel):
    supplier_code: str
    name: str
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None


class SupplierUpdate(BaseModel):
    supplier_code: str | None = None
    name: str | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    status: SupplierStatus | None = None


class SupplierResponse(BaseModel):
    id: UUID
    name: str
    supplier_code: str
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    status: SupplierStatus
    created_at: datetime
    updated_at: datetime
