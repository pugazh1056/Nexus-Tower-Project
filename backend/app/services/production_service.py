from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from app.repositories import (
    production_order_repo,
    product_repo,
    production_bom_repo,
    production_material_requirements_repo,
    production_progress_repo,
    inventory_repo,
)
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

    def get_order_details(self, order_id: str | UUID) -> Optional[Dict[str, Any]]:
        order = self.get_by_id(order_id)
        if not order:
            return None
        product = product_repo.get_by_id(order.get("product_id"))
        return {
            "production_order": order,
            "product": product,
        }

    def get_order_materials(self, order_id: str | UUID) -> Optional[Dict[str, Any]]:
        order = self.get_by_id(order_id)
        if not order:
            return None

        product_id = order.get("product_id")
        target_qty = float(order.get("target_quantity", 1000.0))

        # BOM lookup
        all_boms = production_bom_repo.get_all()
        boms = [b for b in all_boms if str(b.get("finished_product_id")) == str(product_id)]

        # Material requirements lookup
        all_reqs = production_material_requirements_repo.get_all()
        reqs = [r for r in all_reqs if str(r.get("production_order_id")) == str(order_id)]
        reqs_by_comp = {str(r.get("component_product_id")): r for r in reqs}

        # Inventory lookup
        all_inventory = inventory_repo.get_all()
        inv_by_product = {}
        for inv in all_inventory:
            pid = str(inv.get("product_id"))
            on_hand = float(inv.get("quantity_on_hand", inv.get("quantity", 0.0) or 0.0))
            reserved = float(inv.get("quantity_reserved", 0.0) or 0.0)
            avail = max(on_hand - reserved, 0.0)
            inv_by_product[pid] = inv_by_product.get(pid, 0.0) + avail

        material_items = []
        overall_status = "sufficient"

        if not boms and not reqs:
            # Fallback if no specific BOM found in dataset
            return {
                "production_order_id": str(order_id),
                "material_requirements": [],
                "material_status": "sufficient"
            }

        components_to_check = boms if boms else reqs
        for comp in components_to_check:
            comp_id = str(comp.get("component_product_id") or comp.get("product_id"))
            comp_name = comp.get("component_name") or "Raw Material Component"
            req_per_unit = float(comp.get("required_quantity_per_unit", 1.0) if "required_quantity_per_unit" in comp else 1.0)
            req_qty = float(comp.get("required_quantity", req_per_unit * target_qty))
            
            avail_qty = inv_by_product.get(comp_id, 2000.0) # default fallback if unmapped
            shortage = max(req_qty - avail_qty, 0.0)

            status = "sufficient"
            if shortage > 0:
                status = "critical_shortage" if avail_qty == 0 or shortage >= req_qty else "partial_shortage"
                overall_status = "critical_shortage" if status == "critical_shortage" else (
                    "partial_shortage" if overall_status != "critical_shortage" else overall_status
                )

            material_items.append({
                "component_product_id": comp_id,
                "component_name": comp_name,
                "required_quantity": req_qty,
                "available_inventory_quantity": avail_qty,
                "material_shortage": shortage,
                "unit": comp.get("unit", "units"),
                "status": status,
            })

        return {
            "production_order_id": str(order_id),
            "material_requirements": material_items,
            "material_status": overall_status,
        }

    def get_order_progress_details(self, order_id: str | UUID) -> Optional[Dict[str, Any]]:
        order = self.get_by_id(order_id)
        if not order:
            return None

        all_progress = production_progress_repo.get_all()
        prog = next((p for p in all_progress if str(p.get("production_order_id")) == str(order_id)), None)

        planned_qty = float(prog.get("planned_quantity") if prog and prog.get("planned_quantity") is not None else order.get("target_quantity", 0.0))
        produced_qty = float(prog.get("produced_quantity") if prog and prog.get("produced_quantity") is not None else order.get("completed_quantity", 0.0))
        remaining_qty = max(planned_qty - produced_qty, 0.0)
        production_rate = float(prog.get("production_rate", 0.0) if prog else 0.0)
        
        downtime_mins = float(prog.get("downtime_minutes", 0.0) if prog else 0.0)
        downtime_reason = prog.get("downtime_reason") if prog else None
        
        status_val = str(prog.get("status") if prog and prog.get("status") else order.get("status", "planned")).lower()

        # Timing status
        timing_status = "NOT_STARTED"
        if status_val == "completed":
            timing_status = "COMPLETED"
        elif produced_qty > 0 and status_val in ["in_progress", "scheduled"]:
            timing_status = "ON_TRACK" if downtime_mins == 0 else "DELAYED"
        elif status_val == "halted":
            timing_status = "PAUSED"
        elif downtime_mins > 0:
            timing_status = "DELAYED"
        elif status_val == "scheduled":
            timing_status = "ON_TRACK"

        completion_estimate = None
        if production_rate > 0 and remaining_qty > 0:
            completion_estimate = round(remaining_qty / production_rate, 2) # hours remaining

        return {
            "production_order_id": str(order_id),
            "planned_quantity": planned_qty,
            "produced_quantity": produced_qty,
            "remaining_quantity": remaining_qty,
            "production_rate": production_rate,
            "progress_percentage": float(prog.get("progress_percentage", 0.0) if prog else (produced_qty / planned_qty * 100 if planned_qty > 0 else 0.0)),
            "downtime_minutes": downtime_mins,
            "downtime_reason": downtime_reason,
            "planned_start_date": prog.get("planned_start_date") if prog else order.get("start_date"),
            "planned_end_date": prog.get("planned_end_date") if prog else order.get("end_date"),
            "actual_start_date": prog.get("actual_start_date") if prog else None,
            "actual_end_date": prog.get("actual_end_date") if prog else None,
            "status": status_val,
            "timing": {
                "status": timing_status,
                "completion_estimate_hours": completion_estimate,
            }
        }

    def get_order_risk_assessment(self, order_id: str | UUID) -> Optional[Dict[str, Any]]:
        order = self.get_by_id(order_id)
        if not order:
            return None

        materials = self.get_order_materials(order_id)
        progress = self.get_order_progress_details(order_id)

        mat_status = materials.get("material_status", "sufficient")
        timing_status = progress.get("timing", {}).get("status", "ON_TRACK")
        downtime = progress.get("downtime_minutes", 0.0)

        risk_level = "LOW"
        risk_type = "NONE"
        reason = "Order is proceeding within normal operational parameters."

        if mat_status == "critical_shortage":
            risk_level = "CRITICAL"
            risk_type = "FEEDSTOCK_STARVATION"
            reason = "Critical component material shortage threatens complete line starvation."
        elif mat_status == "partial_shortage":
            risk_level = "HIGH"
            risk_type = "FEEDSTOCK_STARVATION"
            reason = "Partial material shortage detected; inventory buffer is constrained."
        elif downtime > 60 or timing_status == "DELAYED":
            risk_level = "MEDIUM"
            risk_type = "DOWNTIME_DELAY"
            reason = f"Line disruption/downtime ({downtime} mins) impacting schedule execution."

        recommendation = "Continue production monitoring."
        expected_outcome = "Batch completed on schedule."
        key_risks = "None identified."

        if risk_type == "FEEDSTOCK_STARVATION":
            recommendation = "Expedite inbound raw material consignment or reallocate buffer stock."
            expected_outcome = "Prevent line stoppage and maintain delivery SLA."
            key_risks = "Potential premium freight costs."
        elif risk_type == "DOWNTIME_DELAY":
            recommendation = "Dispatch maintenance technician to inspect equipment fault and resume line speed."
            expected_outcome = "Restore full operating capacity."
            key_risks = "Extended downtime if replacement parts required."

        return {
            "production_order_id": str(order_id),
            "risk": {
                "level": risk_level,
                "type": risk_type,
                "reason": reason,
            },
            "recommendation": {
                "action": recommendation,
                "reason": reason,
                "expected_outcome": expected_outcome,
                "key_risks": key_risks,
            },
            "materials_analysis": materials,
            "progress_analysis": progress,
        }

    def analyze_production_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = event_data.get("event_id", "EVT-PROD-001")
        event_type = event_data.get("event_type", "PRODUCTION_DISRUPTION")
        entity_id = event_data.get("entity_id")
        
        order = None
        if entity_id:
            order = self.get_by_id(entity_id)
        if not order:
            orders = self.get_all()
            order = orders[0] if orders else {
                "id": "e0000001-0000-0000-0000-000000000001",
                "order_number": "PROD-2026-401",
                "product_id": "a0000001-0000-0000-0000-000000000001",
                "target_quantity": 15000.0,
                "completed_quantity": 0.0,
                "status": "scheduled",
                "line_id": "Line 02",
            }

        order_id = order.get("id")
        materials = self.get_order_materials(order_id)
        progress = self.get_order_progress_details(order_id)
        risk_assess = self.get_order_risk_assessment(order_id)

        return {
            "event_id": event_id,
            "event_type": event_type,
            "source_domain": "Production",
            "entity_id": order_id,
            "production_order": order,
            "material_requirements": materials.get("material_requirements", []),
            "progress": progress,
            "timing": progress.get("timing", {}),
            "risk": risk_assess.get("risk", {}),
            "recommendation": risk_assess.get("recommendation", {}),
        }

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
