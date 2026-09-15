from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.services.alert_service import alert_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    return alert_service.get_all(status=status)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: UUID, current_user: dict = Depends(get_current_user)):
    alt = alert_service.get_by_id(alert_id)
    if not alt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alt


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_in: AlertCreate,
    current_user: dict = Depends(get_current_user),
):
    return alert_service.create_alert(alert_in)


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    alert_update: AlertUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = alert_service.update_alert(alert_id, alert_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return updated
