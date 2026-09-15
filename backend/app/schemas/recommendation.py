from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class RecommendationStatus(str, Enum):
    PROPOSED = "proposed"
    PENDING_AUTHORIZATION = "pending_authorization"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class RecommendationBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    action_type: str = Field(..., max_length=100)
    related_risk_id: Optional[UUID] = None
    expected_impact: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    payload: Dict[str, Any] = Field(default_factory=dict)


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    status: Optional[RecommendationStatus] = None
    applied_at: Optional[datetime] = None


class RecommendationResponse(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    created_at: datetime
    applied_at: Optional[datetime] = None
