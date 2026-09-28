import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.core.supabase import get_supabase
from app.repositories.base import BaseRepository
from app.services.master_orchestrator import master_orchestrator


def test_supabase_config_missing():
    """Test that missing Supabase credentials raise ValueError configuration error."""
    with patch("app.core.supabase.settings") as mock_settings:
        mock_settings.supabase_url = ""
        mock_settings.supabase_key = ""
        # Reset cached client
        import app.core.supabase as sb_mod
        sb_mod.supabase_client = None
        
        with pytest.raises(ValueError, match="SUPABASE_URL and SUPABASE_KEY must be configured"):
            get_supabase()
        sb_mod.supabase_client = None


def test_repository_supabase_failure_returns_503(client):
    """Test that repository operations raise 503 Operational database unavailable when Supabase query fails."""
    repo = BaseRepository("products")
    
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.side_effect = Exception("Connection lost")
    
    with patch("app.repositories.base.get_supabase", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            repo.get_all()
        assert exc_info.value.status_code == 503
        assert "Operational database unavailable" in exc_info.value.detail


def test_no_csv_fallback_on_query_error(client):
    """Test that no CSV fallback occurs when Supabase query fails."""
    repo = BaseRepository("products")
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.side_effect = Exception("Timeout")
    
    with patch("app.repositories.base.get_supabase", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            repo.get_all()
        # Ensure it raised 503 instead of returning fallback list from memory/CSV
        assert exc_info.value.status_code == 503


def test_health_endpoint_connected(client):
    """Test health endpoint reports healthy status when database is connected."""
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.count.return_value.limit.return_value.execute.return_value = MagicMock(data=[{"id": "1"}])
    
    with patch("app.api.routes.health.get_supabase", return_value=mock_client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["database"]["connected"] is True


def test_health_endpoint_disconnected(client):
    """Test health endpoint reports degraded status and 503 when database is unavailable."""
    with patch("app.api.routes.health.get_supabase", side_effect=Exception("DB Down")):
        res = client.get("/api/health")
        assert res.status_code == 503
        data = res.json()
        assert data["status"] == "degraded"
        assert data["database"]["connected"] is False
        assert data["database"]["error"] is not None


def test_master_orchestrator_fails_when_supabase_unavailable():
    """Test that Master Orchestrator fails cleanly when Supabase is unavailable rather than returning mock data."""
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("DB Down")
    
    with patch("app.repositories.base.get_supabase", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            master_orchestrator.process_event({
                "event_id": "EVT-TEST-001",
                "event_type": "SUPPLIER_DELAY",
                "source_domain": "Procurement",
                "entity_type": "purchase_order",
                "entity_id": "PO-001",
                "data": {"supplier_code": "SUP-001", "delay_days": 5}
            })
        assert exc_info.value.status_code == 503
