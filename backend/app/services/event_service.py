from typing import List, Dict, Any, Optional
from uuid import UUID
from app.repositories import event_repo
from app.schemas.event import EventCreate


class EventService:
    def __init__(self):
        self.repo = event_repo

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        events = self.repo.get_all()
        # Sort desc by created_at
        return sorted(events, key=lambda x: x.get("created_at") or "", reverse=True)[:limit]

    def get_by_id(self, event_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(event_id))

    def create_event(self, event_in: EventCreate | Dict[str, Any]) -> Dict[str, Any]:
        data = event_in.model_dump() if hasattr(event_in, "model_dump") else dict(event_in)
        return self.repo.create(data)


event_service = EventService()
