from typing import List, Dict, Any, Optional
from uuid import UUID
from app.repositories import recommendation_repo
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate, RecommendationStatus
from app.services.event_service import event_service


class RecommendationService:
    def __init__(self):
        self.repo = recommendation_repo

    def get_all(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        recs = self.repo.get_all()
        if status:
            recs = [r for r in recs if r.get("status") == status]
        return sorted(recs, key=lambda x: x.get("confidence_score", 0), reverse=True)

    def get_by_id(self, rec_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(rec_id))

    def create_recommendation(self, rec_in: RecommendationCreate | Dict[str, Any]) -> Dict[str, Any]:
        data = rec_in.model_dump() if hasattr(rec_in, "model_dump") else dict(rec_in)
        return self.repo.create(data)

    def update_recommendation(self, rec_id: str | UUID, rec_update: RecommendationUpdate | Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = rec_update.model_dump(exclude_unset=True) if hasattr(rec_update, "model_dump") else dict(rec_update)
        return self.repo.update(str(rec_id), data)

    def approve_recommendation(self, rec_id: str | UUID, user_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        rec = self.get_by_id(rec_id)
        if not rec:
            return None
        updated = self.repo.update(str(rec_id), {"status": RecommendationStatus.APPROVED.value})
        event_service.create_event({
            "event_type": "RECOMMENDATION_APPROVED",
            "domain": updated.get("target_domain", "operations"),
            "source": "control_tower_ui",
            "payload": {
                "recommendation_id": str(rec_id),
                "title": updated.get("title"),
                "approved_by": user_info.get("email") if user_info else "system",
            },
            "severity": "info",
        })
        return updated


recommendation_service = RecommendationService()
