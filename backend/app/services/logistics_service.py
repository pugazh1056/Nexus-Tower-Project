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


from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from app.repositories import (
    shipment_repo,
    shipment_items_repo,
    shipment_receipts_repo,
    shipment_telemetry_repo,
    product_repo,
)
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

    def get_shipment_details(self, shipment_id: str | UUID) -> Optional[Dict[str, Any]]:
        shipment = self.get_by_id(shipment_id)
        if not shipment:
            return None
        items = self.get_shipment_items(shipment_id)
        receipts = self.get_shipment_receipts(shipment_id)
        telemetry = self.get_shipment_telemetry(shipment_id)
        return {
            "shipment": shipment,
            "items": items,
            "receipts": receipts,
            "telemetry": telemetry,
        }

    def get_shipment_items(self, shipment_id: str | UUID) -> List[Dict[str, Any]]:
        all_items = shipment_items_repo.get_all()
        items = [i for i in all_items if str(i.get("shipment_id")) == str(shipment_id)]
        return items

    def get_shipment_receipts(self, shipment_id: str | UUID) -> List[Dict[str, Any]]:
        all_receipts = shipment_receipts_repo.get_all()
        receipts = [r for r in all_receipts if str(r.get("shipment_id")) == str(shipment_id)]
        return receipts

    def get_shipment_telemetry(self, shipment_id: str | UUID) -> Dict[str, Any]:
        all_tel = shipment_telemetry_repo.get_all()
        tels = [t for t in all_tel if str(t.get("shipment_id")) == str(shipment_id)]
        
        if not tels:
            return {
                "telemetry_records": [],
                "cold_chain_status": "UNAVAILABLE",
                "excursion_count": 0,
                "min_observed_temperature": None,
                "max_observed_temperature": None,
            }

        excursions = [t for t in tels if str(t.get("is_excursion")).lower() in ("true", "1")]
        temps = [float(t["temperature"]) for t in tels if t.get("temperature") is not None]
        min_temp = min(temps) if temps else None
        max_temp = max(temps) if temps else None

        status = "NORMAL"
        if excursions:
            status = "EXCURSION"

        return {
            "telemetry_records": tels,
            "cold_chain_status": status,
            "excursion_count": len(excursions),
            "min_observed_temperature": min_temp,
            "max_observed_temperature": max_temp,
        }

    def get_quantity_status(self, shipment_id: str | UUID) -> str:
        receipts = self.get_shipment_receipts(shipment_id)
        if not receipts:
            return "PENDING_RECEIPT"

        has_rejected = any(float(r.get("rejected_quantity", 0) or 0) > 0 for r in receipts)
        has_damaged = any(float(r.get("damaged_quantity", 0) or 0) > 0 for r in receipts)
        is_partial = any(bool(r.get("partial_delivery", False)) or float(r.get("accepted_quantity", 0) or 0) < float(r.get("received_quantity", 0) or 0) for r in receipts)

        if has_rejected:
            return "REJECTED"
        if has_damaged:
            return "DAMAGED"
        if is_partial:
            return "PARTIAL"
        return "FULL"

    def get_delivery_timing(self, shipment_id: str | UUID) -> Dict[str, Any]:
        shipment = self.get_by_id(shipment_id)
        if not shipment:
            return {"status": "UNAVAILABLE"}

        planned = shipment.get("planned_delivery") or shipment.get("expected_delivery") or shipment.get("delivery_date")
        actual = shipment.get("actual_delivery") or shipment.get("received_date")
        status_val = str(shipment.get("status", "")).lower()

        if not planned and not actual:
            return {"status": "UNAVAILABLE", "planned_date": None, "actual_date": None}

        if status_val in ["preparing", "in_transit", "dispatched", "pending"] and not actual:
            return {"status": "PENDING", "planned_date": planned, "actual_date": None}

        if planned and actual:
            try:
                p_date = datetime.fromisoformat(str(planned).replace("Z", "+00:00"))
                a_date = datetime.fromisoformat(str(actual).replace("Z", "+00:00"))
                diff_hours = (a_date - p_date).total_seconds() / 3600.0
                if diff_hours < -2:
                    t_status = "EARLY"
                elif diff_hours > 4:
                    t_status = "LATE"
                else:
                    t_status = "ON_TIME"
                return {"status": t_status, "planned_date": planned, "actual_date": actual}
            except Exception:
                pass

        return {"status": "ON_TIME" if status_val == "delivered" else "PENDING", "planned_date": planned, "actual_date": actual}

    def get_shipment_risk_assessment(self, shipment_id: str | UUID) -> Optional[Dict[str, Any]]:
        shipment = self.get_by_id(shipment_id)
        if not shipment:
            return None

        q_status = self.get_quantity_status(shipment_id)
        timing = self.get_delivery_timing(shipment_id)
        telemetry = self.get_shipment_telemetry(shipment_id)

        risk_level = "LOW"
        risk_type = "NONE"
        reason = "Shipment transit proceeding normally."

        if q_status == "REJECTED" or q_status == "DAMAGED":
            risk_level = "CRITICAL"
            risk_type = "QUALITY_REJECTION"
            reason = f"Goods received with status {q_status}; quality inspection failure."
        elif telemetry.get("cold_chain_status") == "EXCURSION":
            risk_level = "HIGH"
            risk_type = "TEMPERATURE_EXCURSION"
            reason = f"Cold-chain temperature excursion detected ({telemetry.get('excursion_count')} events)."
        elif timing.get("status") == "LATE":
            risk_level = "MEDIUM"
            risk_type = "SHIPMENT_DELAY"
            reason = "Shipment delivery is delayed past planned schedule."
        elif q_status == "PARTIAL":
            risk_level = "MEDIUM"
            risk_type = "PARTIAL_DELIVERY"
            reason = "Inbound shipment delivered partially; quantity shortfall."

        recommendation = "Monitor shipment status."
        exp_outcome = "Successful delivery completion."
        key_risks = "None."

        if risk_type == "QUALITY_REJECTION":
            recommendation = "Quarantine rejected goods and file vendor discrepancy claim."
            exp_outcome = "Vendor credit and replacement order initiated."
            key_risks = "Inventory stockout before replacement arrives."
        elif risk_type == "TEMPERATURE_EXCURSION":
            recommendation = "Quarantine temperature-exposed goods for QA re-inspection."
            exp_outcome = "Prevent compromised cold-chain stock entering production."
            key_risks = "Product wastage and disposal cost."
        elif risk_type == "SHIPMENT_DELAY":
            recommendation = "Contact freight carrier to expedite customs or transit."
            exp_outcome = "Accelerate arrival."
            key_risks = "Plant production line bottleneck."

        return {
            "shipment_id": str(shipment_id),
            "risk": {
                "level": risk_level,
                "type": risk_type,
                "reason": reason,
            },
            "recommendation": {
                "action": recommendation,
                "reason": reason,
                "expected_outcome": exp_outcome,
                "key_risks": key_risks,
            },
            "quantity_status": q_status,
            "timing_status": timing,
            "cold_chain": telemetry,
        }

    def analyze_shipment_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = event_data.get("event_id", "EVT-LOG-001")
        event_type = event_data.get("event_type", "SHIPMENT_DISRUPTION")
        entity_id = event_data.get("entity_id")

        shipment = None
        if entity_id:
            shipment = self.get_by_id(entity_id)
        if not shipment:
            shipments = self.get_all()
            shipment = shipments[0] if shipments else {
                "id": "b0000001-0000-0000-0000-000000000001",
                "tracking_number": "TRK-2026-901",
                "carrier": "SwiftReefer Cold Chain",
                "status": "in_transit",
            }

        shipment_id = shipment.get("id")
        items = self.get_shipment_items(shipment_id)
        receipts = self.get_shipment_receipts(shipment_id)
        telemetry = self.get_shipment_telemetry(shipment_id)
        q_status = self.get_quantity_status(shipment_id)
        timing = self.get_delivery_timing(shipment_id)
        risk_assess = self.get_shipment_risk_assessment(shipment_id)

        return {
            "event_id": event_id,
            "event_type": event_type,
            "source_domain": "Logistics",
            "entity_id": shipment_id,
            "shipment": shipment,
            "items": items,
            "receipts": receipts,
            "receipt_status": {
                "status": q_status,
                "receipt_records": receipts,
            },
            "timing": timing,
            "cold_chain": telemetry,
            "risk": risk_assess.get("risk", {}),
            "recommendation": risk_assess.get("recommendation", {}),
        }


logistics_service = LogisticsService()
