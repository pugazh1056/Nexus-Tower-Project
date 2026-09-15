from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.risk import RiskCreate, RiskUpdate, RiskResponse
from app.services.risk_service import risk_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/risks", tags=["Supply Chain Risks"])


@router.get("/", response_model=List[RiskResponse])
async def list_risks(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    return risk_service.get_all(status=status)


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(risk_id: UUID, current_user: dict = Depends(get_current_user)):
    risk = risk_service.get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk item not found")
    return risk


@router.post("/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(
    risk_in: RiskCreate,
    current_user: dict = Depends(get_current_user),
):
    return risk_service.create_risk(risk_in)


@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: UUID,
    risk_update: RiskUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = risk_service.update_risk(risk_id, risk_update)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk item not found")
    return updated
