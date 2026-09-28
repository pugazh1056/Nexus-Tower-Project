import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.services.forward_impact_service import forward_impact_service
from app.services.backward_impact_service import backward_impact_service
from app.services.master_orchestrator import master_orchestrator


def test_supplier_delay_forward_impact():
    """Test SUPPLIER_DELAY forward impact analysis."""
    event = {
        "event_id": "EVT-TEST-SUP-01",
        "event_type": "SUPPLIER_DELAY",
        "source_domain": "Procurement",
        "entity_type": "purchase_order",
        "entity_id": "PO-89110",
        "data": {"supplier_code": "SUP-001", "delay_days": 5}
    }
    res = forward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-SUP-01"
    assert res["analysis_type"] == "FORWARD"
    assert res["status"] in ["COMPLETED", "NO_SUPPORTED_RELATIONSHIP"]
    if res["status"] == "COMPLETED":
        assert isinstance(res["impacts"], list)
        for impact in res["impacts"]:
            assert "event_id" in impact
            assert "source_domain" in impact
            assert "entity_type" in impact
            assert "entity_id" in impact
            assert "domain" in impact
            assert "impact" in impact


def test_supplier_delay_backward_impact():
    """Test SUPPLIER_DELAY backward impact analysis."""
    event = {
        "event_id": "EVT-TEST-SUP-02",
        "event_type": "SUPPLIER_DELAY",
        "source_domain": "Procurement",
        "entity_type": "purchase_order",
        "entity_id": "PO-89110",
        "data": {"supplier_code": "SUP-001"}
    }
    res = backward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-SUP-02"
    assert res["analysis_type"] == "BACKWARD"
    assert res["status"] in ["COMPLETED", "NO_SUPPORTED_RELATIONSHIP"]
    if res["status"] == "COMPLETED":
        assert isinstance(res["root_causes"], list)
        for rc in res["root_causes"]:
            assert "event_id" in rc
            assert "source_domain" in rc
            assert "entity_type" in rc
            assert "entity_id" in rc
            assert "domain" in rc
            assert "cause" in rc


def test_stock_low_forward_impact():
    """Test STOCK_LOW forward impact analysis."""
    event = {
        "event_id": "EVT-TEST-STOCK-01",
        "event_type": "STOCK_LOW",
        "source_domain": "Inventory",
        "entity_type": "inventory",
        "entity_id": "inv-001",
        "data": {"product_sku": "MILK-001"}
    }
    res = forward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-STOCK-01"
    assert res["analysis_type"] == "FORWARD"
    assert "status" in res


def test_stock_low_backward_impact():
    """Test STOCK_LOW backward impact analysis."""
    event = {
        "event_id": "EVT-TEST-STOCK-02",
        "event_type": "STOCK_LOW",
        "source_domain": "Inventory",
        "entity_type": "inventory",
        "entity_id": "inv-001",
        "data": {"product_sku": "MILK-001"}
    }
    res = backward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-STOCK-02"
    assert res["analysis_type"] == "BACKWARD"
    assert "status" in res


def test_production_disruption_forward_impact():
    """Test PRODUCTION_DISRUPTION forward impact analysis."""
    event = {
        "event_id": "EVT-TEST-PROD-01",
        "event_type": "PRODUCTION_DISRUPTION",
        "source_domain": "Production",
        "entity_type": "production_order",
        "entity_id": "PROD-2026-401",
        "data": {"production_number": "PROD-2026-401"}
    }
    res = forward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-PROD-01"
    assert res["analysis_type"] == "FORWARD"
    assert "status" in res


def test_production_disruption_backward_impact():
    """Test PRODUCTION_DISRUPTION backward impact analysis."""
    event = {
        "event_id": "EVT-TEST-PROD-02",
        "event_type": "PRODUCTION_DISRUPTION",
        "source_domain": "Production",
        "entity_type": "production_order",
        "entity_id": "PROD-2026-401",
        "data": {"production_number": "PROD-2026-401"}
    }
    res = backward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-PROD-02"
    assert res["analysis_type"] == "BACKWARD"
    assert "status" in res


def test_shipment_disruption_forward_impact():
    """Test SHIPMENT_DISRUPTION forward impact analysis."""
    event = {
        "event_id": "EVT-TEST-SHIP-01",
        "event_type": "SHIPMENT_DISRUPTION",
        "source_domain": "Logistics",
        "entity_type": "shipment",
        "entity_id": "TRK-9021",
        "data": {"tracking_number": "TRK-9021"}
    }
    res = forward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-SHIP-01"
    assert res["analysis_type"] == "FORWARD"
    assert "status" in res


def test_shipment_disruption_backward_impact():
    """Test SHIPMENT_DISRUPTION backward impact analysis."""
    event = {
        "event_id": "EVT-TEST-SHIP-02",
        "event_type": "SHIPMENT_DISRUPTION",
        "source_domain": "Logistics",
        "entity_type": "shipment",
        "entity_id": "TRK-9021",
        "data": {"tracking_number": "TRK-9021"}
    }
    res = backward_impact_service.analyze(event)
    assert res["event_id"] == "EVT-TEST-SHIP-02"
    assert res["analysis_type"] == "BACKWARD"
    assert "status" in res


def test_no_supported_relationship():
    """Test handling of unsupported event types and entities."""
    event = {
        "event_id": "EVT-TEST-NONE-01",
        "event_type": "UNKNOWN_EVENT_TYPE",
        "source_domain": "Unknown",
        "entity_type": "unknown",
        "entity_id": "NON-EXISTENT",
        "data": {}
    }
    f_res = forward_impact_service.analyze(event)
    assert f_res["status"] == "NO_SUPPORTED_RELATIONSHIP"
    assert f_res["impacts"] == []

    b_res = backward_impact_service.analyze(event)
    assert b_res["status"] == "NO_SUPPORTED_RELATIONSHIP"
    assert b_res["root_causes"] == []


def test_event_identity_preservation():
    """Test that event identity (event_id, source_domain) is preserved across master orchestrator execution."""
    event = {
        "event_id": "EVT-IDENTITY-999",
        "event_type": "SUPPLIER_DELAY",
        "source_domain": "Procurement",
        "entity_type": "purchase_order",
        "entity_id": "PO-89110",
        "data": {"supplier_code": "SUP-001"}
    }
    result = master_orchestrator.process_event(event)
    assert result["event_id"] == "EVT-IDENTITY-999"
    assert result["source_domain"] == "Procurement"
    assert "forward_impact" in result
    assert "backward_impact" in result
    assert result["forward_impact"]["event_id"] == "EVT-IDENTITY-999"
    assert result["backward_impact"]["event_id"] == "EVT-IDENTITY-999"


def test_supabase_failure_behavior():
    """Test resilience when Supabase throws exception during impact analysis."""
    with patch("app.repositories.base.BaseRepository.get_all", side_effect=Exception("DB Error")):
        event = {
            "event_id": "EVT-FAIL-01",
            "event_type": "SUPPLIER_DELAY",
            "source_domain": "Procurement",
            "entity_type": "purchase_order",
            "entity_id": "PO-001",
            "data": {}
        }
        res = forward_impact_service.analyze(event)
        assert res["status"] == "NO_SUPPORTED_RELATIONSHIP"
        assert res["impacts"] == []


def test_no_sns_webhook_calls():
    """Test that no webhook calls or SNS workbench mechanisms are invoked."""
    event = {
        "event_id": "EVT-WEBHOOK-01",
        "event_type": "SUPPLIER_DELAY",
        "source_domain": "Procurement",
        "entity_type": "purchase_order",
        "entity_id": "PO-89110",
        "data": {}
    }
    with patch("requests.post") as mock_post:
        master_orchestrator.process_event(event)
        mock_post.assert_not_called()


def test_no_csv_fallback():
    """Test that operational impact analysis does not fallback to CSV stores on repository failure."""
    with patch("app.repositories.base.BaseRepository.get_all", side_effect=Exception("Supabase unavailable")):
        res = forward_impact_service.analyze({
            "event_id": "EVT-FALLBACK-01",
            "event_type": "STOCK_LOW",
            "source_domain": "Inventory",
            "entity_type": "inventory",
            "entity_id": "inv-001",
            "data": {}
        })
        # Should return NO_SUPPORTED_RELATIONSHIP rather than returning mock CSV data
        assert res["status"] == "NO_SUPPORTED_RELATIONSHIP"


def test_no_autonomous_database_mutation():
    """Test that running impact analysis does not mutate database tables."""
    # Impact analysis is read-only inspection; verify no insert/update calls are made on repositories
    with patch("app.repositories.base.BaseRepository.create") as mock_create, \
         patch("app.repositories.base.BaseRepository.update") as mock_update:
        master_orchestrator.process_event({
            "event_id": "EVT-MUTATION-01",
            "event_type": "SUPPLIER_DELAY",
            "source_domain": "Procurement",
            "entity_type": "purchase_order",
            "entity_id": "PO-89110",
            "data": {}
        })
        mock_create.assert_not_called()
        mock_update.assert_not_called()
