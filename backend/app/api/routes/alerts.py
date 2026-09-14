"""Alert and exception routes."""

from app.api.routes._resource import resource_router

router = resource_router("/api/alerts", "alerts", "alerts")
