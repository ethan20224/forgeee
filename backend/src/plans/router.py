import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.common.rate_limit import limiter
from src.database.connection import get_db
from src.database.models import User
from src.plans.schemas import GeneratePlanResponse, PlanDetail
from src.plans.service import generate_plan, get_current_plan, get_plan_by_id
from src.quiz.service import get_latest_quiz

router = APIRouter(prefix="/api/v1/plans", tags=["plans"])


@router.post(
    "/generate",
    response_model=GeneratePlanResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("2/hour")
async def generate(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeneratePlanResponse:
    """Generate a 90-day plan from the user's latest quiz answers."""
    quiz = await get_latest_quiz(db, user.id)
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete the quiz before generating a plan.",
        )

    try:
        plan, from_cache = await generate_plan(db, user.id, quiz, season=user.season)
    except (ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Plan generation failed validation: {exc}",
        )

    return GeneratePlanResponse(
        plan=PlanDetail.model_validate(plan),
        from_cache=from_cache,
    )


@router.get("/current", response_model=PlanDetail)
async def current_plan(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanDetail:
    """Get the user's most recent plan."""
    plan = await get_current_plan(db, user.id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plan found. Generate one first.",
        )
    return PlanDetail.model_validate(plan)


@router.get("/{plan_id}", response_model=PlanDetail)
async def get_plan(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanDetail:
    """Get a specific plan by ID."""
    plan = await get_plan_by_id(db, plan_id, user.id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found.",
        )
    return PlanDetail.model_validate(plan)
