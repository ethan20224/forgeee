import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.constants import PILLAR_DB_FIELDS
from src.database.models import DailyTask, PendingTaskEffect, Progress, User

XP_PER_TASK = 10
STREAK_BONUS_XP = 5
STREAK_BONUS_THRESHOLD = 3
DRIFT_PER_TASK = Decimal("0.5")
MAX_PILLAR_SCORE = 100
STREAK_MILESTONES = [7, 14, 30, 60, 90]

XP_LEVEL_THRESHOLDS = [
    0, 100, 250, 500, 850, 1300, 1900, 2600, 3500, 4600,
    5900, 7400, 9200, 11300, 13800, 16700, 20000, 24000, 28500, 34000,
]


def level_from_xp(total_xp: int) -> int:
    """Determine level from total XP using threshold table."""
    level = 1
    for i, threshold in enumerate(XP_LEVEL_THRESHOLDS):
        if total_xp >= threshold:
            level = i + 1
        else:
            break
    return level


async def get_todays_tasks(
    db: AsyncSession,
    user: User,
) -> list[DailyTask]:
    """Fetch tasks for the user's current program day."""
    result = await db.execute(
        select(DailyTask)
        .where(DailyTask.user_id == user.id, DailyTask.day_number == user.program_day)
        .order_by(DailyTask.pillar, DailyTask.title)
    )
    return list(result.scalars().all())


async def complete_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    user: User,
) -> dict:
    """
    Mark a task as completed and apply all side effects:
    XP award, streak update, score drift, pending effect queue.

    Returns a dict with completion details for the response.
    """
    result = await db.execute(
        select(DailyTask).where(DailyTask.id == task_id, DailyTask.user_id == user.id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise TaskNotFoundError(task_id)

    if task.is_completed:
        return _build_idempotent_response(task, user)

    task.is_completed = True
    task.completed_at = datetime.now(UTC)

    progress = await _get_or_create_progress(db, user.id)

    streak_bonus = _calculate_streak_bonus(progress.current_streak)
    xp_earned = XP_PER_TASK + streak_bonus
    progress.total_xp += xp_earned
    progress.level = level_from_xp(progress.total_xp)

    today = date.today()
    streak_milestone = _update_streak(progress, today)

    new_pillar_score = await _apply_drift(db, progress, task)

    await db.flush()

    return {
        "task_id": task.id,
        "xp_earned": xp_earned,
        "streak_bonus": streak_bonus,
        "total_xp": progress.total_xp,
        "new_streak": progress.current_streak,
        "level": progress.level,
        "pillar_affected": task.pillar,
        "new_pillar_score": new_pillar_score,
        "streak_milestone": streak_milestone,
    }


async def get_heatmap(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> dict:
    """Build 90-day completion heatmap from daily_tasks."""
    result = await db.execute(
        select(
            DailyTask.day_number,
            func.count().label("total_tasks"),
            func.count(DailyTask.completed_at).label("completed_tasks"),
            func.min(DailyTask.pillar).label("primary_pillar"),
        )
        .where(DailyTask.user_id == user_id)
        .group_by(DailyTask.day_number)
        .order_by(DailyTask.day_number)
    )
    rows = result.all()

    days = []
    total_completed = 0
    total_tasks = 0
    for row in rows:
        rate = (row.completed_tasks / row.total_tasks * 100) if row.total_tasks > 0 else 0.0
        days.append({
            "day_number": row.day_number,
            "total_tasks": row.total_tasks,
            "completed_tasks": row.completed_tasks,
            "completion_rate": round(rate, 1),
            "primary_pillar": row.primary_pillar,
        })
        total_completed += row.completed_tasks
        total_tasks += row.total_tasks

    overall_rate = (total_completed / total_tasks * 100) if total_tasks > 0 else 0.0

    return {
        "days": days,
        "total_days": len(days),
        "overall_completion_rate": round(overall_rate, 1),
    }


def _calculate_streak_bonus(current_streak: int) -> int:
    """Award bonus XP when streak exceeds threshold."""
    if current_streak > STREAK_BONUS_THRESHOLD:
        return STREAK_BONUS_XP
    return 0


def _update_streak(progress: Progress, today: date) -> int | None:
    """
    Update streak based on last_active_date.
    Returns milestone value if one was just hit, else None.
    """
    if progress.last_active_date == today:
        return None

    if progress.last_active_date is not None:
        days_since = (today - progress.last_active_date).days
        if days_since == 1:
            progress.current_streak += 1
        elif days_since > 1:
            progress.current_streak = 1
    else:
        progress.current_streak = 1

    progress.last_active_date = today

    if progress.current_streak > progress.longest_streak:
        progress.longest_streak = progress.current_streak

    milestone = None
    if progress.current_streak in STREAK_MILESTONES:
        milestone = progress.current_streak

    return milestone


async def _apply_drift(
    db: AsyncSession,
    progress: Progress,
    task: DailyTask,
) -> int:
    """
    Apply +0.5 score drift to the task's pillar, capped at 100.
    Inserts a pending_task_effect before applying for resilience.
    """
    effect = PendingTaskEffect(
        user_id=progress.user_id,
        task_id=task.id,
        pillar=task.pillar,
        drift=DRIFT_PER_TASK,
    )
    db.add(effect)

    field_name = PILLAR_DB_FIELDS.get(task.pillar)
    if field_name is None:
        effect.applied_at = datetime.now(UTC)
        return 0

    current_score = getattr(progress, field_name)
    new_score = min(int(current_score + DRIFT_PER_TASK), MAX_PILLAR_SCORE)
    setattr(progress, field_name, new_score)

    _recalculate_optimisation_score(progress)

    effect.applied_at = datetime.now(UTC)

    return new_score


def _recalculate_optimisation_score(progress: Progress) -> None:
    """Recalculate optimisation score as average of all 9 pillar scores."""
    scores = [
        progress.facial_composition_score,
        progress.skin_score,
        progress.grooming_score,
        progress.hair_score,
        progress.posture_score,
        progress.style_score,
        progress.sleep_score,
        progress.nutrition_score,
        progress.voice_score,
    ]
    avg = sum(scores) / len(scores)
    progress.optimisation_score = Decimal(str(round(avg, 2)))


async def _get_or_create_progress(db: AsyncSession, user_id: uuid.UUID) -> Progress:
    """Get existing progress row or create one with defaults."""
    result = await db.execute(
        select(Progress).where(Progress.user_id == user_id)
    )
    progress = result.scalar_one_or_none()

    if progress is None:
        progress = Progress(user_id=user_id)
        db.add(progress)
        await db.flush()

    return progress


def _build_idempotent_response(task: DailyTask, user: User) -> dict:
    """Return a safe response when task was already completed (idempotency)."""
    return {
        "task_id": task.id,
        "xp_earned": 0,
        "streak_bonus": 0,
        "total_xp": 0,
        "new_streak": 0,
        "level": 1,
        "pillar_affected": task.pillar,
        "new_pillar_score": 0,
        "streak_milestone": None,
    }


class TaskNotFoundError(Exception):
    """Raised when a task is not found for the given user."""

    def __init__(self, task_id: uuid.UUID):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Core business logic for the task engine — fetching today's tasks,
completing tasks with XP/streak/drift side effects, and building heatmap data.

Flow:
1. get_todays_tasks() — queries daily_tasks for user's current program_day
2. complete_task() — marks done, awards XP (+streak bonus), updates streak,
   applies score drift to pillar, inserts pending_task_effect
3. get_heatmap() — aggregates daily_tasks by day_number with completion rates

Main Entry Point: get_todays_tasks, complete_task, get_heatmap

Dependencies:
- sqlalchemy: async DB queries
- src.database.models: DailyTask, Progress, PendingTaskEffect, User
- src.common.constants: PILLAR_DB_FIELDS for dynamic attribute access
"""
