from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    message: Optional[str] = None
    severity: str = "medium"
    source_service: Optional[str] = "system"
    domain: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    entity_id: Optional[UUID] = None

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v):
        if isinstance(v, str):
            return v.lower()
        if hasattr(v, "value"):
            return v.value.lower()
        return "medium"

    @field_validator("description", mode="before")
    @classmethod
    def ensure_description(cls, v, info):
        if v:
            return str(v)
        # fallback to message if description not provided
        data = info.data
        if "message" in data and data["message"]:
            return str(data["message"])
        return "Alert notice"


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None


class AlertResponse(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = "active"
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, str):
            return v.lower()
        if hasattr(v, "value"):
            return v.value.lower()
        return "active"
