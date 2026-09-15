from typing import List, Dict, Any, Optional
from uuid import UUID
from app.repositories import product_repo
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.event_service import event_service


class ProductService:
    def __init__(self):
        self.repo = product_repo

    def get_all(self) -> List[Dict[str, Any]]:
        return self.repo.get_all()

    def get_by_id(self, product_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(product_id))

    def create_product(self, product_in: ProductCreate | Dict[str, Any]) -> Dict[str, Any]:
        data = product_in.model_dump() if hasattr(product_in, "model_dump") else dict(product_in)
        created = self.repo.create(data)
        event_service.create_event({
            "event_type": "PRODUCT_CREATED",
            "domain": "inventory",
            "source": "api",
            "payload": {"product_id": created["id"], "sku": created.get("sku"), "name": created.get("name")},
            "severity": "info",
        })
        return created

    def update_product(self, product_id: str | UUID, product_update: ProductUpdate | Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = product_update.model_dump(exclude_unset=True) if hasattr(product_update, "model_dump") else dict(product_update)
        return self.repo.update(str(product_id), data)

    def delete_product(self, product_id: str | UUID) -> bool:
        return self.repo.delete(str(product_id))


product_service = ProductService()
