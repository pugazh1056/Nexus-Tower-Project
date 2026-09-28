from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentStatus,
)
from app.services.logistics_service import logistics_service
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("/", response_model=List[ShipmentResponse])
async def list_shipments(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    return logistics_service.get_all(status=status)


@router.get("/{shipment_id}/details")
async def get_shipment_details(shipment_id: UUID, current_user: dict = Depends(get_current_user)):
    details = logistics_service.get_shipment_details(shipment_id)
    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return details


@router.get("/{shipment_id}/items")
async def get_shipment_items(shipment_id: UUID, current_user: dict = Depends(get_current_user)):
    shipment = logistics_service.get_by_id(shipment_id)
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return logistics_service.get_shipment_items(shipment_id)


@router.get("/{shipment_id}/receipts")
async def get_shipment_receipts(shipment_id: UUID, current_user: dict = Depends(get_current_user)):
    shipment = logistics_service.get_by_id(shipment_id)
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return logistics_service.get_shipment_receipts(shipment_id)


@router.get("/{shipment_id}/telemetry")
async def get_shipment_telemetry(shipment_id: UUID, current_user: dict = Depends(get_current_user)):
    shipment = logistics_service.get_by_id(shipment_id)
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return logistics_service.get_shipment_telemetry(shipment_id)


@router.get("/{shipment_id}/risk")
async def get_shipment_risk(shipment_id: UUID, current_user: dict = Depends(get_current_user)):
    risk = logistics_service.get_shipment_risk_assessment(shipment_id)
    if not risk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return risk


@router.post("/analyze-event")
async def analyze_shipment_event(
    event_data: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    return logistics_service.analyze_shipment_event(event_data)


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(shipment_id: UUID, current_user: dict = Depends(get_current_user)):
    shipment = logistics_service.get_by_id(shipment_id)
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return shipment


@router.post("/", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    shipment_in: ShipmentCreate,
    current_user: dict = Depends(require_roles(["admin", "logistics"])),
):
    return logistics_service.create_shipment(shipment_in)


@router.put("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: UUID,
    shipment_update: ShipmentUpdate,
    current_user: dict = Depends(require_roles(["admin", "logistics"])),
):
    try:
        updated = logistics_service.update_shipment(shipment_id, shipment_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return updated


@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(
    shipment_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "logistics"])),
):
    try:
        deleted = logistics_service.delete_shipment(shipment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return None
