from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.coaching.schemas import (
    InsightResponse,
    SeasonReportResponse,
    WeeklyReportResponse,
    WeeklyReportSummary,
)
from src.coaching.service import (
    get_daily_insight,
    get_season_report,
    get_weekly_report,
    get_weekly_reports_list,
)
from src.database.connection import get_db
from src.database.models import User

router = APIRouter(prefix="/api/v1/coaching", tags=["coaching"])


@router.get("/daily-insight", response_model=InsightResponse)
async def daily_insight(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InsightResponse:
    """Get today's deterministic coaching insight."""
    data = await get_daily_insight(db, user)
    return InsightResponse(**data)


@router.get("/weekly-report/{week}", response_model=WeeklyReportResponse)
async def weekly_report(
    week: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WeeklyReportResponse:
    """Get a weekly report for the given week number."""
    if week < 1 or week > 13:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Week must be between 1 and 13.",
        )
    data = await get_weekly_report(db, user, week)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekly report not found.",
        )
    return WeeklyReportResponse(**data)


@router.get("/weekly-reports", response_model=list[WeeklyReportSummary])
async def weekly_reports_list(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[WeeklyReportSummary]:
    """List all weekly report summaries for the current season."""
    reports = await get_weekly_reports_list(db, user)
    return [WeeklyReportSummary(**r) for r in reports]


@router.get("/season-report", response_model=SeasonReportResponse)
async def season_report(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SeasonReportResponse:
    """Get end-of-season narrative report."""
    data = await get_season_report(db, user)
    return SeasonReportResponse(**data)


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: FastAPI router for coaching endpoints.

Flow:
1. GET /daily-insight — today's coaching insight (template-based)
2. GET /weekly-report/{week} — full weekly report with coaching paragraphs
3. GET /weekly-reports — list of weekly report summaries
4. GET /season-report — end-of-season narrative

Main Entry Point: router (included in main.py)

Dependencies:
- src.coaching.service: business logic
- src.coaching.schemas: response models
- src.auth.dependencies: JWT auth
"""
