from fastapi import FastAPI
from app.config import settings
from app.api.routes.products import router as products_router
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.suppliers import router as suppliers_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.purchase_orders import router as purchase_orders_router
from app.api.routes.production_orders import router as production_orders_router
from app.api.routes.shipments import router as shipments_router
from app.api.routes.events import router as events_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.risks import router as risks_router
from app.api.routes.recommendations import router as recommendations_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

app.include_router(products_router)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(suppliers_router)
app.include_router(inventory_router)
app.include_router(purchase_orders_router)
app.include_router(production_orders_router)
app.include_router(shipments_router)
app.include_router(events_router)
app.include_router(alerts_router)
app.include_router(risks_router)
app.include_router(recommendations_router)


@app.get("/")
def root():
    return {
        "message": "FMCG Supply Chain API is running",
        "environment": settings.environment
    }