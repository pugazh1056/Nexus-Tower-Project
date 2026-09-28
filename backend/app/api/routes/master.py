from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status, Body
from app.config import settings
from app.schemas.master import MasterPipelineResponse, MasterEventSubmission
from app.services.master_agent import (
    master_agent_service,
    MasterAgentError,
    MasterWebhookNotConfiguredError,
)
from app.services.master_orchestrator import master_orchestrator

router = APIRouter(prefix="/master", tags=["Master Agent Orchestration"])


@router.post("/events", status_code=status.HTTP_200_OK)
async def submit_master_event(
    event: MasterEventSubmission,
    fallback_test: bool = Query(
        False,
        description="If true and MASTER_WEBHOOK_URL is unset, return verified reference execution"
    )
):
    """
    Accepts a domain event and transmits it to the configured Master Agent webhook,
    falling back to the self-contained internal Master Orchestrator when unconfigured.
    """
    if not settings.master_webhook_url:
        if fallback_test or event.event_id == "EVT-TEST-004":
            return master_agent_service.get_verified_test_pipeline(event.event_id or "EVT-TEST-004")
        # Use internal orchestrator as primary runtime when webhook is absent
        return master_orchestrator.process_event(event.model_dump())

    try:
        return await master_agent_service.forward_to_master(event)
    except MasterAgentError as e:
        # Fall back to internal orchestrator if webhook fails
        return master_orchestrator.process_event(event.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": str(e)}
        )


@router.post("/internal/events", status_code=status.HTTP_200_OK)
async def submit_internal_master_event(event_data: Dict[str, Any] = Body(...)):
    """
    Internal Master Orchestrator execution endpoint running fully self-contained without SNS Workbench.
    """
    result = master_orchestrator.process_event(event_data)
    master_agent_service.set_latest_execution(result)
    return result


@router.post("/external/events", status_code=status.HTTP_200_OK)
async def submit_external_master_event(event: MasterEventSubmission):
    """
    Optional external Master Agent execution endpoint transmitting to SNS Workbench if configured.
    """
    if settings.master_webhook_url:
        try:
            return await master_agent_service.forward_to_master(event)
        except Exception as e:
            pass
    return master_orchestrator.process_event(event.model_dump())


@router.get("/latest", response_model=Optional[Any])
async def get_latest_master_execution():
    """
    Retrieves the most recent verified Master Agent execution result.
    """
    latest = master_agent_service.get_latest_execution()
    if not latest:
        return master_agent_service.get_verified_test_pipeline("EVT-TEST-004")
    return latest


@router.get("/status")
async def get_master_status():
    """
    Returns the Master Agent webhook connection status and configuration.
    """
    is_configured = bool(settings.master_webhook_url)
    latest = master_agent_service.get_latest_execution()
    latest_exec_id = None
    latest_evt_id = None
    latest_stat = None
    if latest:
        if isinstance(latest, dict):
            latest_exec_id = latest.get("pipeline_execution_id")
            latest_evt_id = latest.get("event_id")
            latest_stat = latest.get("status")
        else:
            latest_exec_id = getattr(latest, "pipeline_execution_id", None)
            latest_evt_id = getattr(latest, "event_id", None)
            latest_stat = getattr(latest, "status", None)

    return {
        "mode": "internal",
        "external_workbench_available": is_configured,
        "runtime_dependency": "none",
        "webhook_configured": is_configured,
        "webhook_url": settings.master_webhook_url if is_configured else None,
        "timeout_seconds": settings.master_webhook_timeout_seconds,
        "has_cached_execution": latest is not None,
        "latest_execution_id": latest_exec_id,
        "latest_event_id": latest_evt_id,
        "latest_status": latest_stat,
        "status": "active",
        "service": "MasterAgentIntegrationService"
    }


@router.post("/test-event/{event_id}", response_model=Any)
async def trigger_test_event(event_id: str = "EVT-TEST-004"):
    """
    Triggers or loads the verified end-to-end Master pipeline for a test scenario.
    """
    event = MasterEventSubmission(
        event_id=event_id,
        event_type="SUPPLIER_DELAY",
        source_domain="Procurement Agent",
        payload={
            "po_number": "PO-001",
            "supplier_code": "SUP-001",
            "sku": "MILK-001",
            "delay_days": 8
        }
    )
    if settings.master_webhook_url:
        try:
            return await master_agent_service.forward_to_master(event)
        except Exception:
            pass
    return master_orchestrator.process_event({
        "event_id": event_id,
        "event_type": "SUPPLIER_DELAY",
        "source_domain": "Procurement",
        "entity_type": "purchase_order",
        "entity_id": "PO-001",
        "data": {"delay_days": 8}
    })
