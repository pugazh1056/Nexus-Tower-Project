from typing import List, Dict, Any, Optional
from uuid import UUID
from app.repositories import supplier_repo
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.services.event_service import event_service
from app.services.alert_service import alert_service
from app.services.risk_service import risk_service


class SupplierService:
    def __init__(self):
        self.repo = supplier_repo

    def get_all(self) -> List[Dict[str, Any]]:
        return self.repo.get_all()

    def get_by_id(self, supplier_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(supplier_id))

    def create_supplier(self, supplier_in: SupplierCreate | Dict[str, Any]) -> Dict[str, Any]:
        data = supplier_in.model_dump() if hasattr(supplier_in, "model_dump") else dict(supplier_in)
        created = self.repo.create(data)
        event_service.create_event({
            "event_type": "SUPPLIER_REGISTERED",
            "domain": "procurement",
            "source": "api",
            "payload": {"supplier_id": created["id"], "name": created.get("name")},
            "severity": "info",
        })
        return created

    def update_supplier(self, supplier_id: str | UUID, supplier_update: SupplierUpdate | Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = supplier_update.model_dump(exclude_unset=True) if hasattr(supplier_update, "model_dump") else dict(supplier_update)
        return self.repo.update(str(supplier_id), data)

    def delete_supplier(self, supplier_id: str | UUID) -> bool:
        return self.repo.delete(str(supplier_id))

    def report_delay(self, supplier_id: str | UUID, delay_days: int, reason: str) -> Dict[str, Any]:
        supplier = self.get_by_id(supplier_id)
        supplier_name = supplier.get("name", "Unknown Supplier") if supplier else "Unknown Supplier"
        
        # 1. Trigger Event
        evt = event_service.create_event({
            "event_type": "SUPPLIER_DELAY_REPORTED",
            "domain": "procurement",
            "source": "supplier_portal",
            "payload": {
                "supplier_id": str(supplier_id),
                "supplier_name": supplier_name,
                "delay_days": delay_days,
                "reason": reason,
            },
            "severity": "warning" if delay_days < 3 else "high",
        })

        # 2. Trigger Alert
        alert_service.create_alert({
            "title": f"Supplier Delay: {supplier_name}",
            "message": f"{supplier_name} reported delivery slip of +{delay_days} days. Reason: {reason}",
            "severity": "HIGH" if delay_days >= 3 else "MEDIUM",
            "domain": "procurement",
            "entity_type": "supplier",
            "entity_id": str(supplier_id),
            "status": "ACTIVE",
        })

        # 3. Trigger Risk
        risk_service.create_risk({
            "risk_code": f"RSK-SUP-{str(supplier_id)[:6]}",
            "title": f"Lead-time Expansion: {supplier_name}",
            "description": f"Inbound raw material replenishment delayed by {delay_days} days ({reason}).",
            "category": "supply",
            "probability": 0.75,
            "impact_score": 7.0,
            "estimated_loss": delay_days * 1800.0,
            "status": "IDENTIFIED",
        })

        return {"event": evt, "status": "delay_recorded", "delay_days": delay_days}


supplier_service = SupplierService()
