"""Background scheduler jobs — weekly reports, season rollover, day advance."""

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DailyTask, Progress, User, WeeklyReport


async def advance_program_days(db: AsyncSession) -> int:
    """
    Advance program_day for all active users who were active yesterday.

    Runs daily at 00:05 UTC.
    Returns the number of users advanced.
    """
    yesterday = date.today() - timedelta(days=1)
    stmt = (
        update(User)
        .where(
            User.onboarded.is_(True),
            User.last_active_date == yesterday,
        )
        .values(program_day=User.program_day + 1)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount


async def check_season_rollovers(db: AsyncSession) -> int:
    """
    Find users who've reached day 90+ and roll them to the next season.

    Runs daily at 00:10 UTC.
    Returns the number of users rolled over.
    """
    stmt = select(User).where(
        User.onboarded.is_(True),
        User.program_day >= 90,
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    count = 0
    for user in users:
        user.season += 1
        user.program_day = 1
        count += 1

    if count > 0:
        await db.flush()
    return count


async def generate_weekly_reports(db: AsyncSession) -> int:
    """
    Generate weekly reports for users who completed a week.

    Runs Sunday 06:00 UTC.
    Returns the number of reports generated.
    """
    stmt = select(User).where(User.onboarded.is_(True))
    result = await db.execute(stmt)
    users = result.scalars().all()

    count = 0
    for user in users:
        week_number = (user.program_day - 1) // 7 + 1
        if week_number < 1:
            continue

        existing = await db.execute(
            select(WeeklyReport).where(
                WeeklyReport.user_id == user.id,
                WeeklyReport.week_number == week_number,
                WeeklyReport.season == user.season,
            )
        )
        if existing.scalar_one_or_none():
            continue

        report_content = await _build_weekly_report_content(user.id, week_number, db)

        report = WeeklyReport(
            user_id=user.id,
            week_number=week_number,
            season=user.season,
            content=report_content,
        )
        db.add(report)
        count += 1

    if count > 0:
        await db.flush()
    return count


async def check_streaks(db: AsyncSession) -> int:
    """
    Reset streaks for users who didn't complete tasks yesterday.

    Runs daily at 00:15 UTC.
    Returns the number of streaks reset.
    """
    yesterday = date.today() - timedelta(days=1)

    stmt = select(Progress).where(
        Progress.current_streak > 0,
        Progress.last_active_date < yesterday,
    )
    result = await db.execute(stmt)
    stale_progress = result.scalars().all()

    count = 0
    for progress in stale_progress:
        progress.current_streak = 0
        count += 1

    if count > 0:
        await db.flush()
    return count


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _build_weekly_report_content(
    user_id: uuid.UUID, week_number: int, db: AsyncSession
) -> dict:
    """Build a simple weekly report content payload."""
    start_day = (week_number - 1) * 7 + 1
    end_day = week_number * 7

    stmt = select(DailyTask).where(
        DailyTask.user_id == user_id,
        DailyTask.day_number >= start_day,
        DailyTask.day_number <= end_day,
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    total = len(tasks)
    completed = sum(1 for t in tasks if t.is_completed)
    completion_rate = round(completed / total * 100, 1) if total > 0 else 0.0

    pillar_counts: dict[str, int] = {}
    for task in tasks:
        if task.is_completed:
            pillar_counts[task.pillar] = pillar_counts.get(task.pillar, 0) + 1

    return {
        "week_number": week_number,
        "total_tasks": total,
        "completed_tasks": completed,
        "completion_rate": completion_rate,
        "pillar_breakdown": pillar_counts,
        "generated_at": datetime.now(UTC).isoformat(),
    }


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Background scheduler jobs for automated daily/weekly maintenance.

Flow:
1. advance_program_days() — daily bump for active users
2. check_season_rollovers() — find users at day 90+, roll to next season
3. generate_weekly_reports() — idempotent report generation each Sunday
4. check_streaks() — reset streaks for inactive users

Main Entry Point: Each function is called by the scheduler independently

Dependencies:
- src.database.models: User, Progress, WeeklyReport, DailyTask
"""
