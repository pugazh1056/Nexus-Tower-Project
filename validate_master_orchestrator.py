import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.services.master_orchestrator import master_orchestrator

def run_verification():
    print("=" * 60)
    print("VERIFYING SELF-CONTAINED MASTER ORCHESTRATOR")
    print("=" * 60)

    scenarios = [
        {
            "event_id": "EVT-PROC-001",
            "event_type": "SUPPLIER_DELAY",
            "source_domain": "Procurement",
            "entity_type": "purchase_order",
            "entity_id": "PO-001",
            "data": {"supplier_code": "SUP-001", "delay_days": 8}
        },
        {
            "event_id": "EVT-INV-001",
            "event_type": "STOCK_LOW",
            "source_domain": "Inventory",
            "entity_type": "inventory",
            "entity_id": "inv-001",
            "data": {"product_sku": "MILK-001", "quantity_on_hand": 120.0}
        },
        {
            "event_id": "EVT-PROD-001",
            "event_type": "PRODUCTION_DISRUPTION",
            "source_domain": "Production",
            "entity_type": "production_order",
            "entity_id": "e0000001-0000-0000-0000-000000000001",
            "data": {"disruption_type": "FEEDSTOCK_STARVATION"}
        },
        {
            "event_id": "EVT-LOG-001",
            "event_type": "SHIPMENT_DISRUPTION",
            "source_domain": "Logistics",
            "entity_type": "shipment",
            "entity_id": "b0000001-0000-0000-0000-000000000001",
            "data": {"issue_type": "TEMPERATURE_EXCURSION"}
        }
    ]

    for sc in scenarios:
        result = master_orchestrator.process_event(sc)
        print(f"\nScenario: {sc['event_type']} (Primary: {result['primary_domain']})")
        print(f"  - Pipeline Execution ID: {result['pipeline_execution_id']}")
        print(f"  - Affected Domains: {result['affected_domains']}")
        print(f"  - Recommendations Count: {len(result['recommendations'])}")
        print(f"  - Approval Status: {result['approval_status']}")
        assert result['approval_status'] == "PENDING"
        assert result['event_id'] == sc['event_id']

    print("=" * 60)
    print("SUCCESS: ALL MASTER ORCHESTRATOR SCENARIOS PASSED!")

if __name__ == "__main__":
    run_verification()
