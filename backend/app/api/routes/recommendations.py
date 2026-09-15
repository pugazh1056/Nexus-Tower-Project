from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationStatus,
)
from app.services.recommendation_service import recommendation_service
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])


@router.get("/", response_model=List[RecommendationResponse])
async def list_recommendations(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    return recommendation_service.get_all(status=status)


@router.get("/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation(rec_id: UUID, current_user: dict = Depends(get_current_user)):
    rec = recommendation_service.get_by_id(rec_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return rec


@router.post("/", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    rec_in: RecommendationCreate,
    current_user: dict = Depends(get_current_user),
):
    return recommendation_service.create_recommendation(rec_in)


@router.put("/{rec_id}", response_model=RecommendationResponse)
async def update_recommendation(
    rec_id: UUID,
    rec_update: RecommendationUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = recommendation_service.update_recommendation(rec_id, rec_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return updated


@router.post("/{rec_id}/approve", response_model=RecommendationResponse)
async def approve_recommendation(
    rec_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "procurement", "production", "logistics"])),
):
    updated = recommendation_service.approve_recommendation(rec_id, user_info=current_user)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return updated
