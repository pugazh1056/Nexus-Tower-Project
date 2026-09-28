import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.services.procurement_service import procurement_service
from app.services.inventory_service import inventory_service
from app.services.production_service import production_service
from app.services.logistics_service import logistics_service
from app.services.forward_impact_service import forward_impact_service
from app.services.backward_impact_service import backward_impact_service


class MasterOrchestrator:
    def __init__(self):
        pass

    def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = event_data.get("event_id") or f"EVT-MST-{uuid.uuid4().hex[:6].upper()}"
        event_type = event_data.get("event_type") or "SUPPLIER_DELAY"
        source_domain = event_data.get("source_domain") or event_data.get("domain") or "Procurement"
        entity_type = event_data.get("entity_type") or "purchase_order"
        entity_id = event_data.get("entity_id") or event_data.get("data", {}).get("po_id") or "PO-001"
        data = event_data.get("data", {})

        src_lower = source_domain.lower()
        if "procurement" in src_lower or event_type in ["SUPPLIER_DELAY", "PO_CREATED", "PO_ORDERED"]:
            primary_domain = "Procurement"
        elif "inventory" in src_lower or event_type in ["STOCK_LOW", "INVENTORY_LOW"]:
            primary_domain = "Inventory"
        elif "production" in src_lower or event_type in ["PRODUCTION_DISRUPTION"]:
            primary_domain = "Production"
        elif "logistics" in src_lower or event_type in ["SHIPMENT_DISRUPTION"]:
            primary_domain = "Logistics"
        else:
            primary_domain = "Procurement"

        all_domains = ["Procurement", "Inventory", "Production", "Logistics"]
        affected_domains = [d for d in all_domains if d != primary_domain]

        domain_results = []
        recommendations = []

        # Primary domain analysis
        if primary_domain == "Procurement":
            proc_res = procurement_service.analyze_procurement_event({
                "event_id": event_id, "event_type": event_type, "entity_id": entity_id, "data": data
            })
            domain_results.append(proc_res)
            if proc_res.get("recommendation"):
                recommendations.append(proc_res["recommendation"])
        elif primary_domain == "Inventory":
            inv_res = inventory_service.analyze_inventory_event({
                "event_id": event_id, "event_type": event_type, "entity_id": entity_id, "data": data
            })
            domain_results.append(inv_res)
            if inv_res.get("recommendation"):
                recommendations.append(inv_res["recommendation"])
        elif primary_domain == "Production":
            prod_res = production_service.analyze_production_event({
                "event_id": event_id, "event_type": event_type, "entity_type": entity_type, "entity_id": entity_id, "data": data
            })
            domain_results.append(prod_res)
            if prod_res.get("recommendation"):
                rec = prod_res["recommendation"]
                recommendations.append({
                    "domain": "Production",
                    "action": rec.get("action"),
                    "reason": rec.get("reason"),
                    "expected_outcome": rec.get("expected_outcome"),
                    "key_risks": rec.get("key_risks")
                })
        elif primary_domain == "Logistics":
            log_res = logistics_service.analyze_shipment_event({
                "event_id": event_id, "event_type": event_type, "entity_type": entity_type, "entity_id": entity_id, "data": data
            })
            domain_results.append(log_res)
            if log_res.get("recommendation"):
                rec = log_res["recommendation"]
                recommendations.append({
                    "domain": "Logistics",
                    "action": rec.get("action"),
                    "reason": rec.get("reason"),
                    "expected_outcome": rec.get("expected_outcome"),
                    "key_risks": rec.get("key_risks")
                })

        # Affected domains analysis
        for aff in affected_domains:
            if aff == "Inventory":
                inv_res = inventory_service.analyze_inventory_event({
                    "event_id": event_id, "event_type": "AFFECTED_STOCK_CHECK", "entity_id": entity_id, "data": data
                })
                domain_results.append(inv_res)
                if inv_res.get("recommendation"):
                    recommendations.append(inv_res["recommendation"])
            elif aff == "Production":
                prod_res = production_service.analyze_production_event({
                    "event_id": event_id, "event_type": "AFFECTED_PRODUCTION_CHECK", "entity_type": entity_type, "entity_id": entity_id, "data": data
                })
                domain_results.append(prod_res)
                if prod_res.get("recommendation"):
                    rec = prod_res["recommendation"]
                    recommendations.append({
                        "domain": "Production",
                        "action": rec.get("action"),
                        "reason": rec.get("reason"),
                        "expected_outcome": rec.get("expected_outcome"),
                        "key_risks": rec.get("key_risks")
                    })
            elif aff == "Logistics":
                log_res = logistics_service.analyze_shipment_event({
                    "event_id": event_id, "event_type": "AFFECTED_SHIPMENT_CHECK", "entity_type": entity_type, "entity_id": entity_id, "data": data
                })
                domain_results.append(log_res)
                if log_res.get("recommendation"):
                    rec = log_res["recommendation"]
                    recommendations.append({
                        "domain": "Logistics",
                        "action": rec.get("action"),
                        "reason": rec.get("reason"),
                        "expected_outcome": rec.get("expected_outcome"),
                        "key_risks": rec.get("key_risks")
                    })
            elif aff == "Procurement":
                proc_res = procurement_service.analyze_procurement_event({
                    "event_id": event_id, "event_type": "AFFECTED_PROC_CHECK", "entity_id": entity_id, "data": data
                })
                domain_results.append(proc_res)
                if proc_res.get("recommendation"):
                    recommendations.append(proc_res["recommendation"])

        cross_domain_impacts = [
            {
                "from_domain": primary_domain,
                "to_domain": aff,
                "impact_type": "DOWNSTREAM_PROPAGATION",
                "description": f"Disruption in {primary_domain} impacts {aff} operational schedule and inventory runway."
            }
            for aff in affected_domains
        ]

        # Run Forward and Backward Impact Analysis
        forward_res = forward_impact_service.analyze(event_data)
        backward_res = backward_impact_service.analyze(event_data)

        pipeline_execution_id = f"EXEC-MST-20260916-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "pipeline_execution_id": pipeline_execution_id,
            "event_id": event_id,
            "status": "COMPLETED",
            "timestamp": timestamp,
            "source_domain": source_domain,
            "primary_domain": primary_domain,
            "affected_domains": affected_domains,
            "domain_results": domain_results,
            "cross_domain_impacts": cross_domain_impacts,
            "forward_impact": forward_res,
            "backward_impact": backward_res,
            "recommendations": recommendations,
            "approval_status": "PENDING"
        }


master_orchestrator = MasterOrchestrator()
