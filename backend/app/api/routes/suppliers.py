"""Supplier management routes."""

from fastapi import APIRouter, Depends, Response, status

from app.core.dependencies import get_current_user, require_roles
from app.schemas.supplier import SupplierCreate, SupplierResponse, SupplierUpdate
from app.services.crud import create_row, delete_row, get_row, list_rows, update_row

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("/", response_model=list[SupplierResponse], dependencies=[Depends(get_current_user)])
def list_suppliers() -> list[dict]:
    return list_rows("suppliers")


@router.get("/{supplier_id}", response_model=SupplierResponse, dependencies=[Depends(get_current_user)])
def get_supplier(supplier_id: str) -> dict:
    return get_row("suppliers", supplier_id)


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("admin", "procurement"))])
def create_supplier(payload: SupplierCreate) -> dict:
    return create_row("suppliers", payload.model_dump(exclude_none=True))


@router.patch("/{supplier_id}", response_model=SupplierResponse, dependencies=[Depends(require_roles("admin", "procurement"))])
def update_supplier(supplier_id: str, payload: SupplierUpdate) -> dict:
    return update_row("suppliers", supplier_id, payload.model_dump(exclude_unset=True, exclude_none=True))


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin", "procurement"))])
def delete_supplier(supplier_id: str) -> Response:
    delete_row("suppliers", supplier_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
