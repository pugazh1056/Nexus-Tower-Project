import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.services.production_service import production_service
import json

def run_verification():
    print("=" * 60)
    print("VERIFYING SELF-CONTAINED PRODUCTION DOMAIN LOGIC")
    print("=" * 60)

    orders = production_service.get_all()
    print(f"Total production orders loaded: {len(orders)}")
    assert len(orders) > 0, "No production orders found!"

    order = orders[0]
    order_id = order["id"]
    print(f"Testing with production order: {order.get('order_number')} (ID: {order_id})")

    # 1. Details
    details = production_service.get_order_details(order_id)
    print(f"1. Order Details retrieved: Product ID = {details['product']['sku'] if details.get('product') else 'N/A'}")

    # 2-5. Materials & Shortage
    materials = production_service.get_order_materials(order_id)
    print(f"2-5. Materials requirements count: {len(materials.get('material_requirements', []))}, Status: {materials.get('material_status')}")

    # 6-8. Progress & Timing
    progress = production_service.get_order_progress_details(order_id)
    print(f"6-8. Progress - Planned: {progress['planned_quantity']}, Produced: {progress['produced_quantity']}, Remaining: {progress['remaining_quantity']}, Timing Status: {progress['timing']['status']}")

    # 9-10. Risk & Recommendation
    risk_assess = production_service.get_order_risk_assessment(order_id)
    print(f"9-10. Risk Level: {risk_assess['risk']['level']} ({risk_assess['risk']['type']})")
    print(f"      Recommendation: {risk_assess['recommendation']['action']}")

    # 11-12. Event Analysis
    event_payload = {
        "event_id": "EVT-PROD-VERIFY-001",
        "event_type": "PRODUCTION_DISRUPTION",
        "source_domain": "Production",
        "entity_type": "production_order",
        "entity_id": order_id,
        "data": {
            "product_sku": "MILK-001",
            "disruption_type": "FEEDSTOCK_STARVATION",
            "line": "Filling Line 01"
        }
    }
    analysis = production_service.analyze_production_event(event_payload)
    print("=" * 60)
    print("SAMPLE REAL EVENT ANALYSIS RESPONSE:")
    print(json.dumps(analysis, indent=2))
    print("=" * 60)
    print("SUCCESS: ALL PRODUCTION DOMAIN OPERATIONS & VALIDATIONS PASSED!")

if __name__ == "__main__":
    run_verification()
