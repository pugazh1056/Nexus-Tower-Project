def test_list_and_get_shipment_details(client, auth_headers_production):
    res = client.get("/api/shipments/", headers=auth_headers_production)
    assert res.status_code == 200
    shipments = res.json()
    assert isinstance(shipments, list)
    assert len(shipments) >= 1
    shipment_id = shipments[0]["id"]

    # 1. Shipment details retrieval
    det_res = client.get(f"/api/shipments/{shipment_id}/details", headers=auth_headers_production)
    assert det_res.status_code == 200
    det_data = det_res.json()
    assert "shipment" in det_data
    assert "items" in det_data
    assert "receipts" in det_data
    assert "telemetry" in det_data


def test_shipment_items_and_quantities(client, auth_headers_production):
    res = client.get("/api/shipments/", headers=auth_headers_production)
    assert res.status_code == 200
    shipments = res.json()
    shipment_id = shipments[0]["id"]

    # 2. Shipment items & quantities
    items_res = client.get(f"/api/shipments/{shipment_id}/items", headers=auth_headers_production)
    assert items_res.status_code == 200
    items = items_res.json()
    assert isinstance(items, list)
    for item in items:
        assert "ordered_quantity" in item
        assert "shipped_quantity" in item
        assert "unit" in item


def test_shipment_receipts_and_status(client, auth_headers_production):
    res = client.get("/api/shipments/", headers=auth_headers_production)
    assert res.status_code == 200
    shipments = res.json()
    shipment_id = shipments[0]["id"]

    # 3, 4. Receipts & quantity status
    rec_res = client.get(f"/api/shipments/{shipment_id}/receipts", headers=auth_headers_production)
    assert rec_res.status_code == 200
    receipts = rec_res.json()
    assert isinstance(receipts, list)
    for r in receipts:
        assert "received_quantity" in r
        assert "accepted_quantity" in r
        assert "rejected_quantity" in r
        assert "damaged_quantity" in r


def test_shipment_telemetry_and_cold_chain(client, auth_headers_production):
    res = client.get("/api/shipments/", headers=auth_headers_production)
    assert res.status_code == 200
    shipments = res.json()
    shipment_id = shipments[0]["id"]

    # 6, 7. Cold chain telemetry & temperature excursions
    tel_res = client.get(f"/api/shipments/{shipment_id}/telemetry", headers=auth_headers_production)
    assert tel_res.status_code == 200
    tel_data = tel_res.json()
    assert "cold_chain_status" in tel_data
    assert "excursion_count" in tel_data
    assert "telemetry_records" in tel_data


def test_shipment_risk_and_recommendation(client, auth_headers_production):
    res = client.get("/api/shipments/", headers=auth_headers_production)
    assert res.status_code == 200
    shipments = res.json()
    shipment_id = shipments[0]["id"]

    # 8, 9. Logistics risk & recommendation
    risk_res = client.get(f"/api/shipments/{shipment_id}/risk", headers=auth_headers_production)
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert "risk" in risk_data
    assert "level" in risk_data["risk"]
    assert "recommendation" in risk_data
    assert "action" in risk_data["recommendation"]


def test_shipment_event_analysis(client, auth_headers_production):
    res = client.get("/api/shipments/", headers=auth_headers_production)
    shipments = res.json()
    shipment_id = shipments[0]["id"] if shipments else "b0000001-0000-0000-0000-000000000001"

    # 11, 12. Logistics event analysis
    event_payload = {
        "event_id": "EVT-LOG-TEST-001",
        "event_type": "SHIPMENT_DISRUPTION",
        "source_domain": "Logistics",
        "entity_type": "shipment",
        "entity_id": shipment_id,
        "data": {
            "issue_type": "SHIPMENT_DELAY"
        }
    }
    event_res = client.post("/api/shipments/analyze-event", json=event_payload, headers=auth_headers_production)
    assert event_res.status_code == 200
    ev_data = event_res.json()
    assert ev_data["event_id"] == "EVT-LOG-TEST-001"
    assert ev_data["source_domain"] == "Logistics"
    assert "shipment" in ev_data
    assert "items" in ev_data
    assert "receipt_status" in ev_data
    assert "timing" in ev_data
    assert "cold_chain" in ev_data
    assert "risk" in ev_data
    assert "recommendation" in ev_data


def test_missing_shipment_handling(client, auth_headers_production):
    fake_id = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/shipments/{fake_id}/details", headers=auth_headers_production).status_code == 404
    assert client.get(f"/api/shipments/{fake_id}/items", headers=auth_headers_production).status_code == 404
    assert client.get(f"/api/shipments/{fake_id}/receipts", headers=auth_headers_production).status_code == 404
    assert client.get(f"/api/shipments/{fake_id}/telemetry", headers=auth_headers_production).status_code == 404
    assert client.get(f"/api/shipments/{fake_id}/risk", headers=auth_headers_production).status_code == 404
