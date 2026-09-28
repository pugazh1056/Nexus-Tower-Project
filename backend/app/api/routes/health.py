from fastapi import APIRouter, Response, status
from app.config import settings
from app.core.supabase import get_supabase

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check(response: Response):
    db_connected = False
    db_error = None
    try:
        supabase = get_supabase()
        if supabase:
            res = supabase.table("products").select("id", count="exact").limit(1).execute()
            db_connected = True
    except Exception as e:
        db_error = str(e)

    if db_connected:
        response.status_code = status.HTTP_200_OK
        app_status = "healthy"
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        app_status = "degraded"

    return {
        "status": app_status,
        "database": {
            "connected": db_connected,
            "error": db_error if not db_connected else None
        },
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }

