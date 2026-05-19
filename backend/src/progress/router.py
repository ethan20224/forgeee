from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database.connection import get_db
from src.database.models import User
from src.progress.schemas import PillarDetailResponse, ProgressResponse
from src.progress.service import get_pillar_detail, get_progress

router = APIRouter(prefix="/api/v1/progress", tags=["progress"])


@router.get("/", response_model=ProgressResponse)
async def progress_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    """Get full progress snapshot: optimisation score, all pillar scores, XP, streak."""
    data = await get_progress(db, user)
    return ProgressResponse(**data)


@router.get("/pillar/{pillar}", response_model=PillarDetailResponse)
async def pillar_detail(
    pillar: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PillarDetailResponse:
    """Get detailed view of a single pillar: score, weight, rank, task history."""
    data = await get_pillar_detail(db, user, pillar)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pillar '{pillar}' not found.",
        )
    return PillarDetailResponse(**data)


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: FastAPI router for progress endpoints.

Flow:
1. GET / — returns full progress snapshot with optimisation score
2. GET /pillar/{pillar} — returns single pillar deep-dive

Main Entry Point: router (included in main.py)

Dependencies:
- src.progress.service: business logic
- src.progress.schemas: response models
- src.auth.dependencies: JWT auth
"""
