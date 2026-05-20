"""API routes for cycle check-ins (photo upload, analysis, history, compare)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.cycles.schemas import (
    AnalyseRequest,
    CycleAnalysisResponse,
    CycleCompareResponse,
    CycleHistoryResponse,
    EligibilityResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from src.cycles.service import (
    CycleNotEligibleError,
    CycleNotFoundError,
    check_eligibility,
    compare_cycles,
    get_cycle_detail,
    get_history,
    get_upload_url,
    submit_analysis,
)
from src.database.connection import get_db
from src.database.models import User

router = APIRouter(prefix="/api/v1/cycles", tags=["cycles"])


@router.post("/upload-url", response_model=UploadUrlResponse)
async def create_upload_url(
    body: UploadUrlRequest,
    user: User = Depends(get_current_user),
):
    """Generate a presigned URL for direct photo upload to R2."""
    return await get_upload_url(user.id, body.angle)


@router.get("/eligibility", response_model=EligibilityResponse)
async def get_eligibility(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if user is eligible for a new cycle check-in."""
    return await check_eligibility(user.id, db)


@router.post("/analyse", response_model=CycleAnalysisResponse)
async def analyse_cycle(
    body: AnalyseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a photo for AI analysis and create a cycle record."""
    try:
        return await submit_analysis(user.id, body.object_key, body.scan_mode, db)
    except CycleNotEligibleError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )


@router.get("/history", response_model=CycleHistoryResponse)
async def get_cycle_history(
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated cycle history."""
    return await get_history(user.id, db, limit=limit, offset=offset)


@router.get("/{cycle_id}", response_model=CycleAnalysisResponse)
async def get_single_cycle(
    cycle_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single cycle analysis detail."""
    try:
        return await get_cycle_detail(user.id, cycle_id, db)
    except CycleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found",
        )


@router.get("/compare/{current_id}/{previous_id}", response_model=CycleCompareResponse)
async def compare_two_cycles(
    current_id: uuid.UUID,
    previous_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare scores between two cycle check-ins."""
    try:
        return await compare_cycles(user.id, current_id, previous_id, db)
    except CycleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both cycles not found",
        )
