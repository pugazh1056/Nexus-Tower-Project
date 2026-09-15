from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.services.supplier_service import supplier_service
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("/", response_model=List[SupplierResponse])
async def list_suppliers(current_user: dict = Depends(get_current_user)):
    return supplier_service.get_all()


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: UUID, current_user: dict = Depends(get_current_user)):
    sup = supplier_service.get_by_id(supplier_id)
    if not sup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return sup


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_in: SupplierCreate,
    current_user: dict = Depends(require_roles(["admin", "procurement"])),
):
    return supplier_service.create_supplier(supplier_in)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: UUID,
    supplier_update: SupplierUpdate,
    current_user: dict = Depends(require_roles(["admin", "procurement"])),
):
    updated = supplier_service.update_supplier(supplier_id, supplier_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return updated


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: UUID,
    current_user: dict = Depends(require_roles(["admin"])),
):
    deleted = supplier_service.delete_supplier(supplier_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return None


@router.post("/{supplier_id}/report-delay")
async def report_supplier_delay(
    supplier_id: UUID,
    delay_days: int = Body(..., embed=True),
    reason: str = Body(..., embed=True),
    current_user: dict = Depends(require_roles(["admin", "procurement", "logistics"])),
):
    supplier = supplier_service.get_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier_service.report_delay(supplier_id, delay_days, reason)
