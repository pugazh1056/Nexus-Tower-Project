"""Purchase-order routes."""

from app.api.routes._resource import resource_router

router = resource_router("/api/purchase-orders", "purchase orders", "purchase_orders")
