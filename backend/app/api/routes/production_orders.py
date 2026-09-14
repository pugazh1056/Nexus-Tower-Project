"""Production-order routes."""

from app.api.routes._resource import resource_router

router = resource_router("/api/production-orders", "production orders", "production_orders")
