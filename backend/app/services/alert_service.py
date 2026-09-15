from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from app.repositories import alert_repo
from app.schemas.alert import AlertCreate, AlertUpdate, AlertStatus


class AlertService:
    def __init__(self):
        self.repo = alert_repo

    def get_all(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        alerts = self.repo.get_all()
        if status:
            alerts = [a for a in alerts if a.get("status") == status]
        return sorted(alerts, key=lambda x: x.get("created_at") or "", reverse=True)

    def get_by_id(self, alert_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(alert_id))

    def create_alert(self, alert_in: AlertCreate | Dict[str, Any]) -> Dict[str, Any]:
        data = alert_in.model_dump() if hasattr(alert_in, "model_dump") else dict(alert_in)
        entity_id = data.get("entity_id")
        domain = data.get("domain")

        # Avoid duplicate active alert for the exact same entity and domain
        if entity_id:
            existing = [
                a for a in self.repo.get_all()
                if a.get("entity_id") == entity_id and a.get("domain") == domain and a.get("status") == AlertStatus.ACTIVE.value
            ]
            if existing:
                return existing[0]

        return self.repo.create(data)

    def update_alert(self, alert_id: str | UUID, alert_update: AlertUpdate | Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = alert_update.model_dump(exclude_unset=True) if hasattr(alert_update, "model_dump") else dict(alert_update)
        if data.get("status") == AlertStatus.RESOLVED.value:
            data["resolved_at"] = datetime.now(timezone.utc).isoformat()
        return self.repo.update(str(alert_id), data)


alert_service = AlertService()
