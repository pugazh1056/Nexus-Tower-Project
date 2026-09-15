from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from app.repositories import shipment_repo
from app.schemas.shipment import (
    ShipmentStatus,
    VALID_SHIPMENT_TRANSITIONS,
)
from app.services.event_service import event_service
from app.services.alert_service import alert_service
from app.services.risk_service import risk_service


class LogisticsService:
    def __init__(self):
        self.repo = shipment_repo

    def get_all(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        shipments = self.repo.get_all()
        if status:
            shipments = [s for s in shipments if str(s.get("status", "")).lower() == status.lower()]
        return sorted(shipments, key=lambda x: str(x.get("created_at") or ""), reverse=True)

    def get_by_id(self, shipment_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(shipment_id))

    def create_shipment(self, shipment_in: Any) -> Dict[str, Any]:
        data = shipment_in.model_dump() if hasattr(shipment_in, "model_dump") else dict(shipment_in)
        if "po_id" in data and data["po_id"]:
            data["po_id"] = str(data["po_id"])
        data["status"] = ShipmentStatus.PREPARING.value

        created = self.repo.create(data)

        event_service.create_event({
            "event_type": "SHIPMENT_CREATED",
            "source_service": "logistics",
            "entity_id": created["id"],
            "payload": {
                "tracking_number": created.get("tracking_number"),
                "carrier": created.get("carrier"),
            },
        })

        return created

    def update_shipment(
        self, shipment_id: str | UUID, shipment_update: Any
    ) -> Optional[Dict[str, Any]]:
        current = self.get_by_id(shipment_id)
        if not current:
            return None

        data = shipment_update.model_dump(exclude_unset=True) if hasattr(shipment_update, "model_dump") else dict(shipment_update)

        if "status" in data and data["status"]:
            target_status_val = data["status"].value if hasattr(data["status"], "value") else str(data["status"]).lower()
            current_status_val = current.get("status", ShipmentStatus.PREPARING.value)
            if hasattr(current_status_val, "value"):
                current_status_val = current_status_val.value
            current_status_val = str(current_status_val).lower()

            target_status = ShipmentStatus(target_status_val)
            current_status = ShipmentStatus(current_status_val)

            if target_status != current_status:
                allowed_transitions = VALID_SHIPMENT_TRANSITIONS.get(current_status, [])
                if target_status not in allowed_transitions:
                    allowed_names = [s.value for s in allowed_transitions]
                    raise ValueError(
                        f"Cannot transition shipment from '{current_status.value}' to '{target_status.value}'. Allowed transitions: {allowed_names}"
                    )

            data["status"] = target_status.value

            # Trigger operational events based on status
            if target_status == ShipmentStatus.DELAYED:
                event_service.create_event({
                    "event_type": "SHIPMENT_DELAYED",
                    "source_service": "logistics",
                    "entity_id": str(shipment_id),
                    "payload": {
                        "tracking_number": current.get("tracking_number"),
                        "carrier": current.get("carrier"),
                        "notes": data.get("notes") or current.get("notes"),
                    },
                })
                alert_service.create_alert({
                    "title": f"Shipment Delayed: {current.get('tracking_number')}",
                    "description": f"Carrier {current.get('carrier')} reported shipment variance. Destination: {current.get('destination')}.",
                    "severity": "high",
                    "source_service": "logistics",
                    "related_entity_id": str(shipment_id),
                })
                risk_service.create_risk({
                    "title": f"Inbound Freight Delay ({current.get('tracking_number')})",
                    "description": f"Transit bottleneck for carrier {current.get('carrier')}. Estimated delay impact on receiving schedule.",
                    "severity": "high",
                    "impact_score": 7.0,
                    "likelihood_score": 8.0,
                    "related_entity_id": str(shipment_id),
                    "mitigation_plan": "Dispatch secondary reefer carrier or expedite customs clearance.",
                })
            elif target_status == ShipmentStatus.DELIVERED:
                data["actual_delivery"] = datetime.now(timezone.utc).isoformat()
                event_service.create_event({
                    "event_type": "SHIPMENT_DELIVERED",
                    "source_service": "logistics",
                    "entity_id": str(shipment_id),
                    "payload": {"tracking_number": current.get("tracking_number")},
                })

        updated = self.repo.update(str(shipment_id), data)
        return updated

    def delete_shipment(self, shipment_id: str | UUID) -> bool:
        current = self.get_by_id(shipment_id)
        if not current:
            return False
        curr_status = str(current.get("status", "")).lower()
        if curr_status not in [ShipmentStatus.PREPARING.value, ShipmentStatus.CANCELLED.value]:
            raise ValueError(f"Cannot delete shipment in '{curr_status}' status. Only preparing or cancelled shipments can be deleted.")
        return self.repo.delete(str(shipment_id))


logistics_service = LogisticsService()
