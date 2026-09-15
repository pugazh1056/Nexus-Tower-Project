from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from app.schemas.production_order import (
    ProductionOrderCreate,
    ProductionOrderUpdate,
    ProductionOrderResponse,
    ProductionOrderStatus,
)
from app.services.production_service import production_service
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/production-orders", tags=["Production Orders"])


@router.get("/", response_model=List[ProductionOrderResponse])
async def list_production_orders(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    return production_service.get_all(status=status)


@router.get("/{order_id}", response_model=ProductionOrderResponse)
async def get_production_order(order_id: UUID, current_user: dict = Depends(get_current_user)):
    order = production_service.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production order not found")
    return order


@router.post("/", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_production_order(
    order_in: ProductionOrderCreate,
    current_user: dict = Depends(require_roles(["admin", "production"])),
):
    return production_service.create_production_order(order_in)


@router.put("/{order_id}", response_model=ProductionOrderResponse)
async def update_production_order(
    order_id: UUID,
    order_update: ProductionOrderUpdate,
    current_user: dict = Depends(require_roles(["admin", "production"])),
):
    try:
        updated = production_service.update_production_order(order_id, order_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production order not found")
    return updated


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_production_order(
    order_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "production"])),
):
    try:
        deleted = production_service.delete_production_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production order not found")
    return None


@router.post("/{order_id}/report-disruption")
async def report_production_disruption(
    order_id: UUID,
    reason: str = Body(..., embed=True),
    downtime_hours: float = Body(..., embed=True),
    current_user: dict = Depends(require_roles(["admin", "production"])),
):
    order = production_service.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production order not found")
    return production_service.report_disruption(order_id, reason, downtime_hours)
