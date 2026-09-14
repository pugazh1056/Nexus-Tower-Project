"""Supply-chain risk routes."""

from app.api.routes._resource import resource_router

router = resource_router("/api/risks", "risks", "risks")
