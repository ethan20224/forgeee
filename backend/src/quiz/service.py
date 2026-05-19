import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import QuizAnswer
from src.quiz.schemas import QuizSubmitRequest


async def save_quiz_answers(
    db: AsyncSession,
    user_id: uuid.UUID,
    body: QuizSubmitRequest,
) -> QuizAnswer:
    """Persist quiz answers for a user. Returns the created row."""
    answer = QuizAnswer(
        user_id=user_id,
        goals=body.goals,
        routine_level=body.routine_level,
        daily_time=body.daily_time,
        timeline=body.timeline,
        main_concern=body.main_concern,
        age_range=body.age_range,
        has_photo=body.has_photo,
    )
    db.add(answer)
    await db.flush()
    return answer


async def get_latest_quiz(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> QuizAnswer | None:
    """Return the most recent quiz submission for a user, or None."""
    result = await db.execute(
        select(QuizAnswer)
        .where(QuizAnswer.user_id == user_id)
        .order_by(QuizAnswer.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
