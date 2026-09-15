from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from app.repositories import production_order_repo, product_repo
from app.schemas.production_order import (
    ProductionOrderStatus,
    VALID_PRODUCTION_TRANSITIONS,
)
from app.services.event_service import event_service
from app.services.alert_service import alert_service
from app.services.risk_service import risk_service


class ProductionService:
    def __init__(self):
        self.repo = production_order_repo

    def get_all(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        orders = self.repo.get_all()
        if status:
            orders = [o for o in orders if str(o.get("status", "")).lower() == status.lower()]
        return sorted(orders, key=lambda x: str(x.get("created_at") or ""), reverse=True)

    def get_by_id(self, order_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(order_id))

    def create_production_order(self, order_in: Any) -> Dict[str, Any]:
        data = order_in.model_dump() if hasattr(order_in, "model_dump") else dict(order_in)
        data["product_id"] = str(data["product_id"])
        data["status"] = ProductionOrderStatus.PLANNED.value
        data["completed_quantity"] = 0.0

        created = self.repo.create(data)

        event_service.create_event({
            "event_type": "PRODUCTION_ORDER_PLANNED",
            "source_service": "production",
            "entity_id": created["id"],
            "payload": {
                "order_number": created.get("order_number"),
                "target_quantity": created.get("target_quantity"),
            },
        })

        return created

    def update_production_order(
        self, order_id: str | UUID, order_update: Any
    ) -> Optional[Dict[str, Any]]:
        current = self.get_by_id(order_id)
        if not current:
            return None

        data = order_update.model_dump(exclude_unset=True) if hasattr(order_update, "model_dump") else dict(order_update)

        if "status" in data and data["status"]:
            target_status_val = data["status"].value if hasattr(data["status"], "value") else str(data["status"]).lower()
            current_status_val = current.get("status", ProductionOrderStatus.PLANNED.value)
            if hasattr(current_status_val, "value"):
                current_status_val = current_status_val.value
            current_status_val = str(current_status_val).lower()

            target_status = ProductionOrderStatus(target_status_val)
            current_status = ProductionOrderStatus(current_status_val)

            if target_status != current_status:
                allowed_transitions = VALID_PRODUCTION_TRANSITIONS.get(current_status, [])
                if target_status not in allowed_transitions:
                    allowed_names = [s.value for s in allowed_transitions]
                    raise ValueError(
                        f"Cannot transition production order from '{current_status.value}' to '{target_status.value}'. Allowed transitions: {allowed_names}"
                    )

            data["status"] = target_status.value

            if target_status == ProductionOrderStatus.COMPLETED:
                event_service.create_event({
                    "event_type": "BATCH_COMPLETED",
                    "source_service": "production",
                    "entity_id": str(order_id),
                    "payload": {
                        "order_number": current.get("order_number"),
                        "completed_quantity": data.get("completed_quantity", current.get("target_quantity")),
                    },
                })

        updated = self.repo.update(str(order_id), data)
        return updated

    def delete_production_order(self, order_id: str | UUID) -> bool:
        current = self.get_by_id(order_id)
        if not current:
            return False
        curr_status = str(current.get("status", "")).lower()
        if curr_status not in [ProductionOrderStatus.PLANNED.value, ProductionOrderStatus.CANCELLED.value]:
            raise ValueError(f"Cannot delete order in '{curr_status}' status. Only planned or cancelled orders can be deleted.")
        return self.repo.delete(str(order_id))

    def report_disruption(self, order_id: str | UUID, reason: str, downtime_hours: float) -> Dict[str, Any]:
        order = self.get_by_id(order_id)
        order_num = order.get("order_number", "Order") if order else "Order"
        line_id = order.get("line_id", "Production Line") if order else "Production Line"

        self.update_production_order(order_id, {"status": ProductionOrderStatus.HALTED.value})

        event = event_service.create_event({
            "event_type": "MACHINE_BREAKDOWN",
            "source_service": "production",
            "entity_id": str(order_id),
            "payload": {
                "order_number": order_num,
                "line_id": line_id,
                "reason": reason,
                "downtime_hours": downtime_hours,
            },
        })

        alert = alert_service.create_alert({
            "title": f"Production Line Halted: {line_id}",
            "description": f"Downtime estimated {downtime_hours}h for {order_num}. Cause: {reason}",
            "severity": "critical" if downtime_hours >= 4 else "high",
            "source_service": "production",
            "related_entity_id": str(order_id),
        })

        risk = risk_service.create_risk({
            "title": f"Batch Delay Hazard ({order_num})",
            "description": f"Line {line_id} stoppage threatens completion deadline by +{downtime_hours}h.",
            "severity": "high",
            "impact_score": 7.5,
            "likelihood_score": 8.0,
            "related_entity_id": str(order_id),
            "mitigation_plan": "Shift secondary production to parallel packaging line.",
        })

        return {
            "status": "disruption_recorded",
            "order_id": str(order_id),
            "event_id": event.get("id"),
            "alert_id": alert.get("id"),
            "risk_id": risk.get("id"),
        }


production_service = ProductionService()
