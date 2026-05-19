"""Service layer for progress and score endpoints."""

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.constants import PILLAR_DB_FIELDS, PILLAR_LABELS, PILLARS
from src.database.models import DailyTask, Progress, QuizAnswer, User
from src.progress.score_calculator import (
    calculate_optimisation_score,
    derive_initial_weights,
)

BASELINE_SCORE = Decimal("50.00")


async def get_progress(
    db: AsyncSession,
    user: User,
) -> dict:
    """
    Build full progress snapshot: optimisation score, pillar scores, XP, streak.
    Recalculates optimisation score using current weights for accuracy.
    """
    progress = await _get_progress(db, user.id)
    weights = await _get_user_weights(db, user)
    pillar_scores = _extract_pillar_scores(progress)

    opt_score = calculate_optimisation_score(pillar_scores, weights)

    pillar_list = []
    for pillar in PILLARS:
        score = pillar_scores.get(pillar, 50) or 50
        pillar_list.append({
            "pillar": pillar,
            "label": PILLAR_LABELS.get(pillar, pillar),
            "score": score,
            "delta_vs_baseline": score - 50,
            "weight": round(weights.get(pillar, 0), 4),
        })

    return {
        "optimisation_score": opt_score,
        "delta_vs_baseline": opt_score - BASELINE_SCORE,
        "current_streak": progress.current_streak if progress else 0,
        "longest_streak": progress.longest_streak if progress else 0,
        "total_xp": progress.total_xp if progress else 0,
        "level": progress.level if progress else 1,
        "pillar_scores": pillar_list,
    }


async def get_pillar_detail(
    db: AsyncSession,
    user: User,
    pillar: str,
) -> dict | None:
    """
    Deep-dive into a single pillar: score, weight, rank, task history.
    Returns None if pillar is invalid.
    """
    if pillar not in PILLARS:
        return None

    progress = await _get_progress(db, user.id)
    weights = await _get_user_weights(db, user)
    pillar_scores = _extract_pillar_scores(progress)

    score = pillar_scores.get(pillar, 50) or 50
    weight = weights.get(pillar, 0)

    sorted_pillars = sorted(
        PILLARS,
        key=lambda p: (pillar_scores.get(p) or 50),
        reverse=True,
    )
    rank = sorted_pillars.index(pillar) + 1

    tasks_completed = await _count_pillar_tasks_completed(db, user.id, pillar)
    history = await _get_pillar_history(db, user.id, pillar)

    return {
        "pillar": pillar,
        "label": PILLAR_LABELS.get(pillar, pillar),
        "score": score,
        "delta_vs_baseline": score - 50,
        "weight": round(weight, 4),
        "rank": rank,
        "tasks_completed": tasks_completed,
        "history": history,
    }


async def _get_progress(db: AsyncSession, user_id: uuid.UUID) -> Progress | None:
    """Fetch progress row for user."""
    result = await db.execute(
        select(Progress).where(Progress.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _get_user_weights(db: AsyncSession, user: User) -> dict[str, float]:
    """Derive user's current pillar weights from face shape + quiz concern."""
    main_concern = await _get_main_concern(db, user.id)
    return derive_initial_weights(
        face_shape=user.face_shape,
        main_concern=main_concern,
        season=user.season,
    )


async def _get_main_concern(db: AsyncSession, user_id: uuid.UUID) -> str | None:
    """Get user's most recent quiz main_concern answer."""
    result = await db.execute(
        select(QuizAnswer.main_concern)
        .where(QuizAnswer.user_id == user_id)
        .order_by(QuizAnswer.created_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    return row


def _extract_pillar_scores(progress: Progress | None) -> dict[str, int | None]:
    """Extract 9 pillar scores from progress row as a dict."""
    if progress is None:
        return {p: 50 for p in PILLARS}

    scores: dict[str, int | None] = {}
    for pillar, field in PILLAR_DB_FIELDS.items():
        scores[pillar] = getattr(progress, field, 50)
    return scores


async def _count_pillar_tasks_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    pillar: str,
) -> int:
    """Count completed tasks for a specific pillar."""
    result = await db.execute(
        select(func.count())
        .select_from(DailyTask)
        .where(
            DailyTask.user_id == user_id,
            DailyTask.pillar == pillar,
            DailyTask.is_completed.is_(True),
        )
    )
    return result.scalar_one()


async def _get_pillar_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    pillar: str,
) -> list[dict]:
    """
    Build score history for a pillar from completed task days.
    Each point represents the cumulative drift from completed tasks.
    """
    result = await db.execute(
        select(DailyTask.day_number)
        .where(
            DailyTask.user_id == user_id,
            DailyTask.pillar == pillar,
            DailyTask.is_completed.is_(True),
        )
        .order_by(DailyTask.day_number)
    )
    days = result.scalars().all()

    history = []
    running_score = 50
    for day in days:
        running_score = min(running_score + 0.5, 100)
        history.append({
            "day_number": day,
            "score": int(running_score),
        })

    return history


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Service layer for progress endpoints. Orchestrates score
calculation by fetching user data, deriving weights, and building responses.

Flow:
1. get_progress() — full snapshot with recalculated optimisation score
2. get_pillar_detail() — single pillar deep-dive with rank and history
3. Helper functions fetch progress, derive weights, count tasks

Main Entry Point: get_progress, get_pillar_detail

Dependencies:
- src.progress.score_calculator: weight derivation and score calculation
- src.database.models: Progress, DailyTask, QuizAnswer, User
- src.common.constants: PILLARS, PILLAR_DB_FIELDS, PILLAR_LABELS
"""
