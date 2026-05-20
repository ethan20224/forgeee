"""API routes for gamification (achievements, challenges, streak, XP)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database.connection import get_db
from src.database.models import User
from src.gamification.schemas import (
    AchievementsResponse,
    ChallengeResponse,
    ChallengesListResponse,
    StartChallengeRequest,
    StreakResponse,
    XPResponse,
)
from src.gamification.service import (
    ChallengeAlreadyActiveError,
    ChallengeNotFoundError,
    get_achievements,
    get_challenges,
    get_streak_info,
    get_xp_info,
    start_challenge,
)

router = APIRouter(prefix="/api/v1/gamification", tags=["gamification"])


@router.get("/achievements", response_model=AchievementsResponse)
async def list_achievements(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all badges with unlock status."""
    return await get_achievements(user.id, db)


@router.get("/challenges", response_model=ChallengesListResponse)
async def list_challenges(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active and available challenges."""
    return await get_challenges(user.id, db)


@router.post("/challenges/start", response_model=ChallengeResponse)
async def start_new_challenge(
    body: StartChallengeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new challenge."""
    try:
        result = await start_challenge(user.id, body, db)
        await db.commit()
        return result
    except ChallengeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
    except ChallengeAlreadyActiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Challenge is already active",
        )


@router.get("/streak", response_model=StreakResponse)
async def get_streak(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current streak info and milestones."""
    return await get_streak_info(user.id, db)


@router.get("/xp", response_model=XPResponse)
async def get_xp(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get XP and level progression."""
    return await get_xp_info(user.id, db)
