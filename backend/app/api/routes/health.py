from fastapi import APIRouter

router = APIRouter(
    prefix="/api/health",
    tags=["Health"]
)


@router.get("/", include_in_schema=True)
def health_check():
    return {
        "status": "ok"
    }