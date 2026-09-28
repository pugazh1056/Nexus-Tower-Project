def test_list_and_get_production_orders(client, auth_headers_production):
    res = client.get("/api/production-orders/", headers=auth_headers_production)
    assert res.status_code == 200
    orders = res.json()
    assert isinstance(orders, list)
    assert len(orders) >= 1
    order_id = orders[0]["id"]

    # 1. Production order retrieval (Details)
    det_res = client.get(f"/api/production-orders/{order_id}/details", headers=auth_headers_production)
    assert det_res.status_code == 200
    det_data = det_res.json()
    assert "production_order" in det_data
    assert "product" in det_data


def test_production_materials_and_shortage(client, auth_headers_production):
    res = client.get("/api/production-orders/", headers=auth_headers_production)
    assert res.status_code == 200
    orders = res.json()
    order_id = orders[0]["id"]

    # 2, 3, 4, 5. BOM, material requirements, inventory availability, material shortage calculation
    mat_res = client.get(f"/api/production-orders/{order_id}/materials", headers=auth_headers_production)
    assert mat_res.status_code == 200
    mat_data = mat_res.json()
    assert "material_requirements" in mat_data
    assert "material_status" in mat_data
    for req in mat_data["material_requirements"]:
        assert "required_quantity" in req
        assert "available_inventory_quantity" in req
        assert "material_shortage" in req
        assert req["material_shortage"] >= 0


def test_production_progress_and_remaining(client, auth_headers_production):
    res = client.get("/api/production-orders/", headers=auth_headers_production)
    assert res.status_code == 200
    orders = res.json()
    order_id = orders[0]["id"]

    # 6, 7, 8. Progress calculation, remaining quantity, timing status
    prog_res = client.get(f"/api/production-orders/{order_id}/progress", headers=auth_headers_production)
    assert prog_res.status_code == 200
    prog_data = prog_res.json()
    assert "planned_quantity" in prog_data
    assert "produced_quantity" in prog_data
    assert "remaining_quantity" in prog_data
    assert prog_data["remaining_quantity"] >= 0
    assert "timing" in prog_data
    assert "status" in prog_data["timing"]


def test_production_risk_and_recommendation(client, auth_headers_production):
    res = client.get("/api/production-orders/", headers=auth_headers_production)
    assert res.status_code == 200
    orders = res.json()
    order_id = orders[0]["id"]

    # 9, 10. Risk detection & recommendation generation
    risk_res = client.get(f"/api/production-orders/{order_id}/risk", headers=auth_headers_production)
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert "risk" in risk_data
    assert "level" in risk_data["risk"]
    assert "recommendation" in risk_data
    assert "action" in risk_data["recommendation"]


def test_production_event_analysis(client, auth_headers_production):
    res = client.get("/api/production-orders/", headers=auth_headers_production)
    orders = res.json()
    order_id = orders[0]["id"] if orders else "e0000001-0000-0000-0000-000000000001"

    # 12. Production event analysis
    event_payload = {
        "event_id": "EVT-PROD-TEST-001",
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
    event_res = client.post("/api/production-orders/analyze-event", json=event_payload, headers=auth_headers_production)
    assert event_res.status_code == 200
    ev_data = event_res.json()
    assert ev_data["event_id"] == "EVT-PROD-TEST-001"
    assert ev_data["source_domain"] == "Production"
    assert "material_requirements" in ev_data
    assert "progress" in ev_data
    assert "timing" in ev_data
    assert "risk" in ev_data
    assert "recommendation" in ev_data


def test_missing_production_order_handling(client, auth_headers_production):
    # 11. Missing/invalid data handling
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/production-orders/{fake_id}/details", headers=auth_headers_production).status_code == 404
    assert client.get(f"/api/production-orders/{fake_id}/materials", headers=auth_headers_production).status_code == 404
    assert client.get(f"/api/production-orders/{fake_id}/progress", headers=auth_headers_production).status_code == 404
    assert client.get(f"/api/production-orders/{fake_id}/risk", headers=auth_headers_production).status_code == 404
