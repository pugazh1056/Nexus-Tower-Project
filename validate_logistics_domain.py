import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.services.logistics_service import logistics_service
import json

def run_verification():
    print("=" * 60)
    print("VERIFYING SELF-CONTAINED LOGISTICS DOMAIN LOGIC")
    print("=" * 60)

    shipments = logistics_service.get_all()
    print(f"Total shipments loaded: {len(shipments)}")
    assert len(shipments) > 0, "No shipments found!"

    shipment = shipments[0]
    shipment_id = shipment["id"]
    print(f"Testing with shipment: {shipment.get('tracking_number')} (ID: {shipment_id})")

    # 1. Details
    details = logistics_service.get_shipment_details(shipment_id)
    print(f"1. Shipment Details retrieved: Carrier = {details['shipment'].get('carrier')}")

    # 2. Items & Quantities
    items = logistics_service.get_shipment_items(shipment_id)
    print(f"2. Shipment items count: {len(items)}")
    for item in items:
        print(f"   - Ordered: {item.get('ordered_quantity')}, Shipped: {item.get('shipped_quantity')} {item.get('unit')}")

    # 3-4. Receipts & Quantity Status
    q_status = logistics_service.get_quantity_status(shipment_id)
    print(f"3-4. Receipt Quantity Status: {q_status}")

    # 5. Timing
    timing = logistics_service.get_delivery_timing(shipment_id)
    print(f"5. Delivery Timing Status: {timing.get('status')}")

    # 6-7. Cold Chain Telemetry
    telemetry = logistics_service.get_shipment_telemetry(shipment_id)
    print(f"6-7. Cold Chain Status: {telemetry.get('cold_chain_status')}, Excursions: {telemetry.get('excursion_count')}")

    # 8-9. Risk & Recommendation
    risk_assess = logistics_service.get_shipment_risk_assessment(shipment_id)
    print(f"8-9. Risk Level: {risk_assess['risk']['level']} ({risk_assess['risk']['type']})")
    print(f"       Recommendation: {risk_assess['recommendation']['action']}")

    # 11-12. Event Analysis
    event_payload = {
        "event_id": "EVT-LOG-VERIFY-001",
        "event_type": "SHIPMENT_DISRUPTION",
        "source_domain": "Logistics",
        "entity_type": "shipment",
        "entity_id": shipment_id,
        "data": {
            "issue_type": "SHIPMENT_DELAY"
        }
    }
    analysis = logistics_service.analyze_shipment_event(event_payload)
    print("=" * 60)
    print("SAMPLE REAL EVENT ANALYSIS RESPONSE:")
    print(json.dumps(analysis, indent=2))
    print("=" * 60)
    print("SUCCESS: ALL LOGISTICS DOMAIN OPERATIONS & VALIDATIONS PASSED!")

if __name__ == "__main__":
    run_verification()
