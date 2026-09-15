from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.event import EventCreate, EventResponse
from app.services.event_service import event_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/events", tags=["Operational Events"])


@router.get("/", response_model=List[EventResponse])
async def list_events(
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
):
    return event_service.get_all(limit=limit)


@router.get("/workbench-feed")
async def workbench_telemetry_feed(current_user: dict = Depends(get_current_user)):
    """Integration feed for SNS Agent Workbench agents."""
    events = event_service.get_all(limit=50)
    return {
        "status": "active",
        "agent_contract_version": "1.0",
        "feed_type": "operational_events",
        "event_count": len(events),
        "events": events,
    }


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: UUID, current_user: dict = Depends(get_current_user)):
    evt = event_service.get_by_id(event_id)
    if not evt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return evt


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_in: EventCreate,
    current_user: dict = Depends(get_current_user),
):
    return event_service.create_event(event_in)
