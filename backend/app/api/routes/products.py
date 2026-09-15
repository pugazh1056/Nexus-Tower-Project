from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import product_service
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(current_user: dict = Depends(get_current_user)):
    return product_service.get_all()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, current_user: dict = Depends(get_current_user)):
    prod = product_service.get_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return prod


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    current_user: dict = Depends(require_roles(["admin", "procurement", "inventory"])),
):
    return product_service.create_product(product_in)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    current_user: dict = Depends(require_roles(["admin", "procurement", "inventory"])),
):
    updated = product_service.update_product(product_id, product_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user: dict = Depends(require_roles(["admin"])),
):
    deleted = product_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return None
