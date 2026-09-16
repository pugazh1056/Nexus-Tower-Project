import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import httpx

from app.schemas.master import MasterPipelineResponse, MasterEventInput


def test_get_master_status(client: TestClient, auth_headers_admin):
    """Test retrieving the Master Agent connection and webhook configuration status."""
    response = client.get("/api/master/status", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "webhook_configured" in data
    assert "service" in data
    assert data["service"] == "MasterAgentIntegrationService"


def test_get_latest_master_execution(client: TestClient, auth_headers_admin):
    """Test retrieving the latest verified Master Agent pipeline execution."""
    response = client.get("/api/master/latest", headers=auth_headers_admin)
    assert response.status_code == 200
    data = response.json()

    # Validate high-level contract
    assert "pipeline_execution_id" in data
    assert "event_id" in data
    assert data["status"] == "COMPLETED"
    assert "timestamp" in data
    assert "stages" in data

    stages = data["stages"]
    # Check all 8 verified pipeline stages
    assert "normalization" in stages
    assert "priority" in stages
    assert "backward_impact" in stages
    assert "forward_impact" in stages
    assert "demand_forecasting_gate" in stages
    assert "decision_optimization" in stages
    assert "smart_replenishment" in stages
    assert "execution_boundary" in stages

    # Check normalization fields
    norm = stages["normalization"]
    assert norm["source_domain"] == "Procurement Agent"
    assert norm["event_type"] == "SUPPLIER_DELAY"
    assert norm["entity_id"] == "PO-001"
    assert norm["supplier"]["name"] == "Dairy Pure Co"
    assert norm["delay_parameters"]["delay_days"] == 8

    # Check priority fields
    prio = stages["priority"]
    assert prio["severity"] == "HIGH"
    assert prio["urgency_score"] == 92.4
    assert prio["sla_impact"] == "BREACH_IMMINENT"

    # Check decision optimization & evaluated options
    opt = stages["decision_optimization"]
    assert len(opt["evaluated_options"]) >= 3
    assert opt["selected_recommendation"]["confidence_score"] >= 0.90

    # Check execution boundary governance
    exec_b = stages["execution_boundary"]
    assert exec_b["execution_mode"] == "HUMAN_IN_THE_LOOP"
    assert "Operations Lead" in exec_b["authorized_roles"]
    assert len(exec_b["executable_actions"]) > 0


def test_trigger_master_test_event_evt004(client: TestClient, auth_headers_admin):
    """Test triggering EVT-TEST-004 through the Master pipeline endpoint."""
    response = client.post(
        "/api/master/test-event/EVT-TEST-004",
        headers=auth_headers_admin,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "EVT-TEST-004"
    assert data["status"] == "COMPLETED"
    assert data["stages"]["normalization"]["entity_id"] == "PO-001"


def test_trigger_master_test_event_invalid(client: TestClient, auth_headers_admin):
    """Test requesting an unsupported test event ID."""
    response = client.post(
        "/api/master/test-event/EVT-UNKNOWN-999",
        headers=auth_headers_admin,
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_submit_master_event_unconfigured_fallback(client: TestClient, auth_headers_admin):
    """Test submitting a domain event when MASTER_WEBHOOK_URL is not configured (returns fallback reference pipeline)."""
    event_payload = {
        "event_id": "EVT-TEST-004",
        "domain": "Procurement",
        "event_type": "SupplierDelayDetected",
        "severity": "HIGH",
        "data": {
            "po_number": "PO-001",
            "supplier_name": "Dairy Pure Co",
            "delay_days": 8,
            "sku": "MILK-001",
        },
    }

    response = client.post(
        "/api/master/events",
        json=event_payload,
        headers=auth_headers_admin,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "pipeline_execution_id" in data


def test_submit_master_event_webhook_timeout(client: TestClient, auth_headers_admin):
    """Test Master Agent webhook timeout handling."""
    with patch("app.services.master_agent.master_agent_service.webhook_url", "https://mock-master.internal/webhook"):
        with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Connection timed out")):
            event_payload = {
                "event_id": "EVT-TIMEOUT-001",
                "domain": "Procurement",
                "event_type": "SupplierDelayDetected",
                "severity": "HIGH",
                "data": {},
            }
            response = client.post(
                "/api/master/events",
                json=event_payload,
                headers=auth_headers_admin,
            )
            assert response.status_code == 504
            assert "timeout" in response.json()["detail"].lower()


def test_submit_master_event_webhook_network_error(client: TestClient, auth_headers_admin):
    """Test Master Agent webhook connection failure handling."""
    with patch("app.services.master_agent.master_agent_service.webhook_url", "https://mock-master.internal/webhook"):
        with patch("httpx.AsyncClient.post", side_effect=httpx.RequestError("Host unreachable")):
            event_payload = {
                "event_id": "EVT-CONN-001",
                "domain": "Procurement",
                "event_type": "SupplierDelayDetected",
                "severity": "HIGH",
                "data": {},
            }
            response = client.post(
                "/api/master/events",
                json=event_payload,
                headers=auth_headers_admin,
            )
            assert response.status_code == 502
            assert "failed to connect" in response.json()["detail"].lower()


def test_submit_master_event_webhook_success(client: TestClient, auth_headers_admin):
    """Test successful Master Agent webhook response parsing and schema validation."""
    mock_master_response = {
        "pipeline_execution_id": "EXEC-WEBHOOK-999",
        "event_id": "EVT-HOOK-001",
        "status": "COMPLETED",
        "timestamp": "2026-09-15T19:00:00Z",
        "stages": {
            "normalization": {
                "source_domain": "Procurement Agent",
                "event_type": "SUPPLIER_DELAY",
                "entity_id": "PO-001",
                "supplier": {"name": "Dairy Pure Co", "supplier_code": "SUP-001"},
                "product": {"sku": "MILK-001", "name": "Fresh Cow Milk"},
                "delay_parameters": {
                    "delay_days": 8,
                    "original_expected_date": "2026-09-06",
                    "revised_expected_date": "2026-09-14",
                },
            },
            "priority": {
                "severity": "HIGH",
                "urgency_score": 92.4,
                "sla_impact": "BREACH_IMMINENT",
                "justification": "8-day delay on primary feedstock.",
            },
            "backward_impact": {
                "root_cause": "Refrigeration breakdown",
                "historical_supplier_performance": {
                    "on_time_delivery_rate": 0.75,
                    "total_historical_orders": 4,
                },
                "contract_audit": {
                    "contract_id": "CTR-001",
                    "sla_minimum": 0.95,
                    "applicable_penalty_amount": 800.0,
                },
            },
            "forward_impact": {
                "affected_domains": ["Inventory", "Production", "Logistics"],
                "inventory_impact": {
                    "current_available_quantity": 30.0,
                    "runway_hours": 28.8,
                    "deficit": 70.0,
                },
                "production_impact": {
                    "affected_order_id": "PRD-2026-001",
                    "material_shortage": 795.0,
                },
                "logistics_fulfillment_impact": {
                    "estimated_revenue_at_risk": 14200.0,
                },
            },
            "demand_forecasting_gate": {
                "sku": "MILK-001",
                "daily_consumption_rate": 25.0,
                "projected_7_day_demand": 175.0,
                "projected_14_day_demand": 350.0,
                "safety_stock_threshold": 100.0,
                "gate_status": "THRESHOLD_BREACHED",
                "decision_gate": "PASSED_TO_OPTIMIZER",
            },
            "decision_optimization": {
                "evaluated_options": [
                    {
                        "option_id": "OPT-1",
                        "strategy": "EXPEDITE_ALTERNATIVE_SUPPLIER",
                        "cost": 1200.0,
                        "production_downtime_loss": 0.0,
                        "net_financial_impact": 13000.0,
                        "otif_projection": 0.98,
                        "score": 94.5,
                    }
                ],
                "selected_recommendation": {
                    "action_strategy": "EXPEDITE_ALTERNATIVE_SUPPLIER",
                    "title": "Emergency Feedstock Reallocation",
                    "description": "Secure alternative supplier volume.",
                    "confidence_score": 0.96,
                    "net_protected_value": 13000.0,
                },
            },
            "smart_replenishment": {
                "status": "PROPOSED_PENDING_APPROVAL",
                "supplier": {"name": "Apex Dairy Farms", "supplier_code": "SUP-005"},
                "replenishment_item": {
                    "sku": "RAW-MILK-01",
                    "name": "Raw Pasteurization Feedstock",
                    "quantity": 800.0,
                    "unit": "Liters",
                    "unit_price": 37.0,
                    "total_amount": 29600.0,
                },
                "requisition_id": "REQ-001",
            },
            "execution_boundary": {
                "execution_mode": "HUMAN_IN_THE_LOOP",
                "authorized_roles": ["Operations Director", "Procurement Manager"],
                "status": "AWAITING_AUTHORIZATION",
                "executable_actions": [
                    {
                        "action_type": "CREATE_PURCHASE_ORDER",
                        "endpoint": "/api/purchase-orders/",
                        "method": "POST",
                        "payload": {"po_number": "PO-EMERGENCY-001"},
                    }
                ],
            },
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_master_response

    with patch("app.services.master_agent.master_agent_service.webhook_url", "https://mock-master.internal/webhook"):
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            event_payload = {
                "event_id": "EVT-HOOK-001",
                "domain": "Procurement",
                "event_type": "SupplierDelayDetected",
                "severity": "HIGH",
                "data": {},
            }
            response = client.post(
                "/api/master/events",
                json=event_payload,
                headers=auth_headers_admin,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["pipeline_execution_id"] == "EXEC-WEBHOOK-999"
            assert data["stages"]["decision_optimization"]["selected_recommendation"]["confidence_score"] == 0.96
