import pytest
from fastapi.testclient import TestClient


def test_master_orchestrator_supplier_delay(client: TestClient, auth_headers_admin):
    event_payload = {
        "event_id": "EVT-PROC-001",
        "event_type": "SUPPLIER_DELAY",
        "source_domain": "Procurement",
        "entity_type": "purchase_order",
        "entity_id": "PO-001",
        "data": {
            "supplier_code": "SUP-001",
            "product_sku": "MILK-001",
            "delay_days": 8
        }
    }
    response = client.post("/api/master/internal/events", json=event_payload, headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "EVT-PROC-001"
    assert data["source_domain"] == "Procurement"
    assert data["primary_domain"] == "Procurement"
    assert "affected_domains" in data
    assert "Inventory" in data["affected_domains"]
    assert "Production" in data["affected_domains"]
    assert "Logistics" in data["affected_domains"]
    assert len(data["domain_results"]) >= 1
    assert len(data["recommendations"]) >= 1
    assert data["approval_status"] == "PENDING"
    assert "pipeline_execution_id" in data


def test_master_orchestrator_stock_low(client: TestClient, auth_headers_admin):
    event_payload = {
        "event_id": "EVT-INV-001",
        "event_type": "STOCK_LOW",
        "source_domain": "Inventory",
        "entity_type": "inventory",
        "entity_id": "inv-001",
        "data": {
            "product_sku": "MILK-001",
            "quantity_on_hand": 120.0
        }
    }
    response = client.post("/api/master/internal/events", json=event_payload, headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "EVT-INV-001"
    assert data["primary_domain"] == "Inventory"
    assert "Procurement" in data["affected_domains"]
    assert data["approval_status"] == "PENDING"


def test_master_orchestrator_production_disruption(client: TestClient, auth_headers_admin):
    event_payload = {
        "event_id": "EVT-PROD-001",
        "event_type": "PRODUCTION_DISRUPTION",
        "source_domain": "Production",
        "entity_type": "production_order",
        "entity_id": "e0000001-0000-0000-0000-000000000001",
        "data": {
            "disruption_type": "FEEDSTOCK_STARVATION"
        }
    }
    response = client.post("/api/master/internal/events", json=event_payload, headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "EVT-PROD-001"
    assert data["primary_domain"] == "Production"
    assert data["approval_status"] == "PENDING"


def test_master_orchestrator_shipment_disruption(client: TestClient, auth_headers_admin):
    event_payload = {
        "event_id": "EVT-LOG-001",
        "event_type": "SHIPMENT_DISRUPTION",
        "source_domain": "Logistics",
        "entity_type": "shipment",
        "entity_id": "b0000001-0000-0000-0000-000000000001",
        "data": {
            "issue_type": "TEMPERATURE_EXCURSION"
        }
    }
    response = client.post("/api/master/internal/events", json=event_payload, headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "EVT-LOG-001"
    assert data["primary_domain"] == "Logistics"
    assert data["approval_status"] == "PENDING"


def test_master_status_reports_internal_mode(client: TestClient, auth_headers_admin):
    response = client.get("/api/master/status", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data.get("mode") == "internal"
    assert data.get("runtime_dependency") == "none"
    assert "external_workbench_available" in data
