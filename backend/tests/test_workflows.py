def test_purchase_order_workflow(client, auth_headers_procurement):
    # 1. Get a product and supplier
    prods = client.get("/api/products/", headers=auth_headers_procurement).json()
    sups = client.get("/api/suppliers/", headers=auth_headers_procurement).json()
    prod_id = prods[0]["id"]
    sup_id = sups[0]["id"]

    # 2. Create PO in 'draft'
    po_payload = {
        "po_number": "PO-TEST-0099",
        "supplier_id": sup_id,
        "items": [
            {"product_id": prod_id, "quantity": 1000.0, "unit_price": 2.50}
        ],
        "notes": "Urgent test batch",
    }
    create_res = client.post("/api/purchase-orders/", json=po_payload, headers=auth_headers_procurement)
    assert create_res.status_code == 201
    po = create_res.json()
    po_id = po["id"]
    assert po["status"] == "draft"
    assert po["total_amount"] == 2500.0

    # 3. Valid transition: draft -> pending_approval
    res1 = client.put(f"/api/purchase-orders/{po_id}", json={"status": "pending_approval"}, headers=auth_headers_procurement)
    assert res1.status_code == 200
    assert res1.json()["status"] == "pending_approval"

    # 4. Invalid transition: pending_approval -> received (should fail with 400)
    bad_res = client.put(f"/api/purchase-orders/{po_id}", json={"status": "received"}, headers=auth_headers_procurement)
    assert bad_res.status_code == 400

    # 5. Valid transition: pending_approval -> approved
    res2 = client.put(f"/api/purchase-orders/{po_id}", json={"status": "approved"}, headers=auth_headers_procurement)
    assert res2.status_code == 200
    assert res2.json()["status"] == "approved"

    # 6. Valid transition: approved -> ordered
    res3 = client.put(f"/api/purchase-orders/{po_id}", json={"status": "ordered"}, headers=auth_headers_procurement)
    assert res3.status_code == 200
    assert res3.json()["status"] == "ordered"

    # 7. Valid transition: ordered -> received
    res4 = client.put(f"/api/purchase-orders/{po_id}", json={"status": "received"}, headers=auth_headers_procurement)
    assert res4.status_code == 200
    assert res4.json()["status"] == "received"


def test_production_order_workflow(client, auth_headers_production):
    prods = client.get("/api/products/", headers=auth_headers_production).json()
    prod_id = prods[0]["id"]

    order_payload = {
        "order_number": "PROD-TEST-77",
        "product_id": prod_id,
        "target_quantity": 5000.0,
        "line_id": "Line 01",
    }
    create_res = client.post("/api/production-orders/", json=order_payload, headers=auth_headers_production)
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    # Invalid: planned -> completed (should fail with 400)
    bad_res = client.put(f"/api/production-orders/{order_id}", json={"status": "completed"}, headers=auth_headers_production)
    assert bad_res.status_code == 400

    # Valid: planned -> scheduled
    res1 = client.put(f"/api/production-orders/{order_id}", json={"status": "scheduled"}, headers=auth_headers_production)
    assert res1.status_code == 200
    assert res1.json()["status"] == "scheduled"

    # Valid: scheduled -> in_progress
    res2 = client.put(f"/api/production-orders/{order_id}", json={"status": "in_progress"}, headers=auth_headers_production)
    assert res2.status_code == 200
    assert res2.json()["status"] == "in_progress"

    # Report disruption
    disrupt_res = client.post(
        f"/api/production-orders/{order_id}/report-disruption",
        json={"reason": "Hydraulic seal rupture on capping head", "downtime_hours": 3.5},
        headers=auth_headers_production,
    )
    assert disrupt_res.status_code == 200
    assert disrupt_res.json()["status"] == "disruption_recorded"

    # Resume to in_progress from halted
    resume_res = client.put(f"/api/production-orders/{order_id}", json={"status": "in_progress"}, headers=auth_headers_production)
    assert resume_res.status_code == 200

    # Valid: in_progress -> completed
    res3 = client.put(f"/api/production-orders/{order_id}", json={"status": "completed", "completed_quantity": 5000.0}, headers=auth_headers_production)
    assert res3.status_code == 200
    assert res3.json()["status"] == "completed"


def test_shipment_delay_triggers_alert_and_risk(client, auth_headers_logistics):
    ship_payload = {
        "tracking_number": "TRK-TEST-9988",
        "carrier": "Midwest Express Reefer",
        "origin": "Green Bay Terminal",
        "destination": "Chicago Packaging Plant",
    }
    create_res = client.post("/api/shipments/", json=ship_payload, headers=auth_headers_logistics)
    assert create_res.status_code == 201
    ship_id = create_res.json()["id"]

    # Transition to dispatched
    client.put(f"/api/shipments/{ship_id}", json={"status": "dispatched"}, headers=auth_headers_logistics)

    # Transition to delayed -> triggers alert, risk, event
    delay_res = client.put(
        f"/api/shipments/{ship_id}",
        json={"status": "delayed", "notes": "Winter storm highway closure"},
        headers=auth_headers_logistics,
    )
    assert delay_res.status_code == 200
    assert delay_res.json()["status"] == "delayed"

    # Verify alert exists
    alerts_res = client.get("/api/alerts/", headers=auth_headers_logistics)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert any("TRK-TEST-9988" in a["title"] for a in alerts)


def test_recommendation_approval(client, auth_headers_admin):
    recs = client.get("/api/recommendations/", headers=auth_headers_admin).json()
    assert len(recs) >= 1
    rec_id = recs[0]["id"]

    approve_res = client.post(f"/api/recommendations/{rec_id}/approve", headers=auth_headers_admin)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"].lower() == "approved"


def test_workbench_feed(client, auth_headers_admin):
    feed_res = client.get("/api/events/workbench-feed", headers=auth_headers_admin)
    assert feed_res.status_code == 200
    data = feed_res.json()
    assert data["feed_type"] == "operational_events"
    assert data["event_count"] >= 1
    assert "events" in data
