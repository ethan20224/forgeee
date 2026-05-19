from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database.connection import get_db
from src.database.models import User
from src.quiz.estimator import full_estimate
from src.quiz.schemas import QuizAnswerResponse, QuizSubmitRequest, ScoreEstimateResponse
from src.quiz.service import get_latest_quiz, save_quiz_answers

router = APIRouter(prefix="/api/v1/quiz", tags=["quiz"])


@router.post(
    "/submit",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_quiz(
    body: QuizSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizAnswerResponse:
    """Save quiz answers for the authenticated user."""
    answer = await save_quiz_answers(db, user.id, body)
    return QuizAnswerResponse.model_validate(answer)


@router.get("/estimate-score", response_model=ScoreEstimateResponse)
async def estimate_score(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ScoreEstimateResponse:
    """Compute a deterministic score estimate from the user's latest quiz answers."""
    quiz = await get_latest_quiz(db, user.id)
    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No quiz answers found. Submit the quiz first.",
        )

    result = full_estimate(
        goals=quiz.goals or [],
        routine_level=quiz.routine_level or "none",
        daily_time=quiz.daily_time or "20min",
        main_concern=quiz.main_concern or "overall",
        age_range=quiz.age_range or "25-29",
        has_photo=quiz.has_photo,
    )
    return ScoreEstimateResponse(**result)
