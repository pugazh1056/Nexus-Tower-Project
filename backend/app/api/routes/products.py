from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import require_roles, require_supabase
from app.schemas.product import (
    ProductResponse,
    ProductCreate,
    ProductUpdate
)
router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.get("/", response_model=list[ProductResponse])
def get_products():
    response = require_supabase().table("products").select("*").execute()
    return response.data


@router.post("/", response_model=ProductResponse, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_product(product: ProductCreate):
    response = (
        require_supabase()
        .table("products")
        .insert(product.model_dump())
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=400,
            detail="Failed to create product"
        )

    return response.data[0]
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    response = (
        require_supabase()
        .table("products")
        .select("*")
        .eq("id", product_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return response.data[0]
@router.patch("/{product_id}", response_model=ProductResponse, dependencies=[Depends(require_roles("admin"))])
def update_product(product_id: str, product: ProductUpdate):
    update_data = product.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    response = (
        require_supabase()
        .table("products")
        .update(update_data)
        .eq("id", product_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return response.data[0]
@router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_product(product_id: str):
    response = (
        require_supabase()
        .table("products")
        .delete()
        .eq("id", product_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )