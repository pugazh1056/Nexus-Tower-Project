from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class EventBase(BaseModel):
    event_type: str = Field(..., max_length=100)
    source_service: str = Field(..., max_length=100)
    entity_id: Optional[UUID] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    timestamp: datetime
    domain: Optional[str] = None
    severity: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize source -> source_service
            if "source_service" not in data and "source" in data:
                data["source_service"] = data["source"]
            elif "source_service" not in data:
                data["source_service"] = data.get("domain", "system")

            # Normalize created_at -> timestamp
            if "timestamp" not in data and "created_at" in data:
                data["timestamp"] = data["created_at"]
        elif hasattr(data, "__dict__"):
            d = data.__dict__
            if not getattr(data, "source_service", None) and hasattr(data, "source"):
                setattr(data, "source_service", getattr(data, "source"))
            if not getattr(data, "timestamp", None) and hasattr(data, "created_at"):
                setattr(data, "timestamp", getattr(data, "created_at"))
        return data

