from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
