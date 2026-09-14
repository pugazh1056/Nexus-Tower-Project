"""Inventory and stock-level routes."""

from app.api.routes._resource import resource_router

router = resource_router("/api/inventory", "inventory", "inventory")
