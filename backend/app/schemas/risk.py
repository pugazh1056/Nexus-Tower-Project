from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"


class RiskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    severity: str = "medium"
    impact_score: float = Field(default=5.0, ge=0.0, le=10.0)
    likelihood_score: float = Field(default=5.0, ge=0.0, le=10.0)
    related_entity_id: Optional[UUID] = None
    mitigation_plan: Optional[str] = None

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v):
        if isinstance(v, str):
            return v.lower()
        if hasattr(v, "value"):
            return v.value.lower()
        return "medium"


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    severity: Optional[str] = None
    impact_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    likelihood_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    mitigation_plan: Optional[str] = None
    status: Optional[str] = None


class RiskResponse(RiskBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = "identified"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, str):
            return v.lower()
        if hasattr(v, "value"):
            return v.value.lower()
        return "identified"
