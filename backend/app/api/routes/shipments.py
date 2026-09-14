"""Shipment and logistics routes."""

from app.api.routes._resource import resource_router

router = resource_router("/api/shipments", "shipments", "shipments")
