from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderStatus,
)
from app.services.procurement_service import procurement_service
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.get("/", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    return procurement_service.get_all(status=status)


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(po_id: UUID, current_user: dict = Depends(get_current_user)):
    po = procurement_service.get_by_id(po_id)
    if not po:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    return po


@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    po_in: PurchaseOrderCreate,
    current_user: dict = Depends(require_roles(["admin", "procurement"])),
):
    return procurement_service.create_purchase_order(po_in)


@router.put("/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    po_id: UUID,
    po_update: PurchaseOrderUpdate,
    current_user: dict = Depends(require_roles(["admin", "procurement", "inventory"])),
):
    try:
        updated = procurement_service.update_purchase_order(po_id, po_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    return updated


@router.delete("/{po_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(
    po_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "procurement"])),
):
    try:
        deleted = procurement_service.delete_purchase_order(po_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found")
    return None
