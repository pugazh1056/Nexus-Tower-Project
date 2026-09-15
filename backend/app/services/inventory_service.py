from typing import List, Dict, Any, Optional
from uuid import UUID
from app.repositories import inventory_repo, product_repo
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.services.event_service import event_service
from app.services.alert_service import alert_service
from app.services.recommendation_service import recommendation_service


class InventoryService:
    def __init__(self):
        self.repo = inventory_repo

    def get_all(self) -> List[Dict[str, Any]]:
        return self.repo.get_all()

    def get_by_id(self, inv_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(inv_id))

    def _check_inventory_rules(self, record: Dict[str, Any]):
        qty_on_hand = float(record.get("quantity_on_hand", 0))
        threshold = float(record.get("reorder_threshold", 0))
        inv_id = str(record.get("id"))
        prod_id = str(record.get("product_id"))

        # Look up product
        product = product_repo.get_by_id(prod_id)
        prod_name = product.get("name", "Product") if product else "Product"

        if threshold > 0 and qty_on_hand <= threshold:
            severity = "CRITICAL" if qty_on_hand <= (threshold * 0.5) else "HIGH"
            
            # 1. Trigger Alert
            alert_service.create_alert({
                "title": f"Low Inventory Alert: {prod_name}",
                "message": f"{record.get('location', 'Warehouse')} stock level ({qty_on_hand} {record.get('unit', '')}) is at or below reorder threshold ({threshold}).",
                "severity": severity,
                "domain": "inventory",
                "entity_type": "inventory",
                "entity_id": inv_id,
                "status": "ACTIVE",
            })

            # 2. Trigger Event
            event_service.create_event({
                "event_type": "INVENTORY_LOW",
                "domain": "inventory",
                "source": "wms_sensor",
                "payload": {
                    "inventory_id": inv_id,
                    "product_id": prod_id,
                    "product_name": prod_name,
                    "quantity_on_hand": qty_on_hand,
                    "reorder_threshold": threshold,
                    "location": record.get("location"),
                },
                "severity": severity.lower(),
            })

            # 3. Create Recommendation if critical
            if severity == "CRITICAL":
                recommendation_service.create_recommendation({
                    "telemetry_id": f"REC-RESTOCK-{inv_id[:6]}",
                    "title": f"Automated Restock Recommendation for {prod_name}",
                    "description": f"Trigger emergency replenishment PO of {threshold - qty_on_hand + 5000} {record.get('unit', '')} to avert plant starvation.",
                    "target_domain": "procurement",
                    "mitigation_cost": 350.0,
                    "net_protected_value": 9800.0,
                    "confidence_score": 96.5,
                    "status": "PENDING_AUTHORIZATION",
                    "steps": [
                        f"Verify stock count at {record.get('location')}",
                        f"Generate expedited purchase order for {prod_name}",
                        "Notify plant logistics manager",
                    ],
                })

    def create_inventory(self, inv_in: InventoryCreate | Dict[str, Any]) -> Dict[str, Any]:
        data = inv_in.model_dump() if hasattr(inv_in, "model_dump") else dict(inv_in)
        # Convert UUID to str
        if "product_id" in data:
            data["product_id"] = str(data["product_id"])
        created = self.repo.create(data)
        self._check_inventory_rules(created)
        return created

    def update_inventory(self, inv_id: str | UUID, inv_update: InventoryUpdate | Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = inv_update.model_dump(exclude_unset=True) if hasattr(inv_update, "model_dump") else dict(inv_update)
        updated = self.repo.update(str(inv_id), data)
        if updated:
            self._check_inventory_rules(updated)
        return updated

    def delete_inventory(self, inv_id: str | UUID) -> bool:
        return self.repo.delete(str(inv_id))


inventory_service = InventoryService()
