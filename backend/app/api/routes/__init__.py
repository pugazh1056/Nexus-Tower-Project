from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .products import router as products_router
from .suppliers import router as suppliers_router
from .inventory import router as inventory_router
from .purchase_orders import router as purchase_orders_router
from .production_orders import router as production_orders_router
from .shipments import router as shipments_router
from .events import router as events_router
from .alerts import router as alerts_router
from .risks import router as risks_router
from .recommendations import router as recommendations_router
from .master import router as master_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(suppliers_router)
api_router.include_router(inventory_router)
api_router.include_router(purchase_orders_router)
# Also include underscore alias for compatibility
api_router.include_router(purchase_orders_router, prefix="/purchase_orders", include_in_schema=False)
api_router.include_router(production_orders_router)
api_router.include_router(production_orders_router, prefix="/production_orders", include_in_schema=False)
api_router.include_router(shipments_router)
api_router.include_router(events_router)
api_router.include_router(alerts_router)
api_router.include_router(risks_router)
api_router.include_router(recommendations_router)
api_router.include_router(master_router)

__all__ = ["api_router"]
