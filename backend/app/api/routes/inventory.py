from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse
from app.services.inventory_service import inventory_service
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/", response_model=List[InventoryResponse])
async def list_inventory(current_user: dict = Depends(get_current_user)):
    return inventory_service.get_all()


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory_item(inventory_id: UUID, current_user: dict = Depends(get_current_user)):
    item = inventory_service.get_by_id(inventory_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return item


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    inv_in: InventoryCreate,
    current_user: dict = Depends(require_roles(["admin", "inventory"])),
):
    return inventory_service.create_inventory(inv_in)


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory_item(
    inventory_id: UUID,
    inv_update: InventoryUpdate,
    current_user: dict = Depends(require_roles(["admin", "inventory"])),
):
    updated = inventory_service.update_inventory(inventory_id, inv_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return updated


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    inventory_id: UUID,
    current_user: dict = Depends(require_roles(["admin"])),
):
    deleted = inventory_service.delete_inventory(inventory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return None
