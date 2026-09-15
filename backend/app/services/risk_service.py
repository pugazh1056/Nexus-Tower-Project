from typing import List, Dict, Any, Optional
from uuid import UUID
from app.repositories import risk_repo
from app.schemas.risk import RiskCreate, RiskUpdate, RiskStatus


class RiskService:
    def __init__(self):
        self.repo = risk_repo

    def get_all(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        risks = self.repo.get_all()
        if status:
            risks = [r for r in risks if r.get("status") == status]
        return sorted(risks, key=lambda x: x.get("probability", 0) * x.get("impact_score", 0), reverse=True)

    def get_by_id(self, risk_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(risk_id))

    def create_risk(self, risk_in: RiskCreate | Dict[str, Any]) -> Dict[str, Any]:
        data = risk_in.model_dump() if hasattr(risk_in, "model_dump") else dict(risk_in)
        return self.repo.create(data)

    def update_risk(self, risk_id: str | UUID, risk_update: RiskUpdate | Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = risk_update.model_dump(exclude_unset=True) if hasattr(risk_update, "model_dump") else dict(risk_update)
        return self.repo.update(str(risk_id), data)


risk_service = RiskService()
