"""Coaching service: deterministic template-based insights and reports.

Zero LLM calls — all coaching content generated from templates + user data.
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.coaching.language_stage import stage_for_day
from src.coaching.season_templates import (
    BIGGEST_MOVER_PARAGRAPHS,
    NEEDS_WORK_PARAGRAPHS,
    NEXT_FOCUS_PARAGRAPHS,
    OPENING_PARAGRAPHS,
)
from src.coaching.templates import DAILY_INSIGHT_TEMPLATES
from src.coaching.weekly_templates import COACHING_PARAGRAPHS, FOCUS_PARAGRAPHS
from src.common.constants import PILLAR_DB_FIELDS, PILLAR_LABELS, PILLARS
from src.database.models import DailyTask, Progress, User, WeeklyReport


async def get_daily_insight(
    db: AsyncSession,
    user: User,
) -> dict:
    """Generate a deterministic daily insight from templates."""
    stage = stage_for_day(user.program_day)
    progress = await _get_progress(db, user.id)

    context_type, pillar, variables = _determine_context(progress, user.program_day)

    template_key = (stage, context_type, pillar)
    templates = DAILY_INSIGHT_TEMPLATES.get(template_key)

    if templates is None and pillar is not None:
        template_key = (stage, context_type, None)
        templates = DAILY_INSIGHT_TEMPLATES.get(template_key)

    if templates is None:
        template_key = (stage, "completion_rate", None)
        templates = DAILY_INSIGHT_TEMPLATES.get(template_key, [])

    if not templates:
        message = f"Day {user.program_day}: Keep building consistency across all pillars."
    else:
        index = user.program_day % len(templates)
        message = templates[index].format(**variables)

    return {
        "stage": stage,
        "context_type": context_type,
        "pillar": pillar,
        "message": message,
        "program_day": user.program_day,
    }


async def get_weekly_report(
    db: AsyncSession,
    user: User,
    week_number: int,
) -> dict | None:
    """Generate or fetch a weekly report for the given week."""
    existing = await _get_stored_report(db, user.id, week_number, user.season)
    if existing:
        return existing

    start_day = (week_number - 1) * 7 + 1
    end_day = week_number * 7

    result = await db.execute(
        select(
            func.count().label("total"),
            func.count(DailyTask.completed_at).label("completed"),
        )
        .where(
            DailyTask.user_id == user.id,
            DailyTask.day_number >= start_day,
            DailyTask.day_number <= end_day,
        )
    )
    row = result.one()
    total_tasks = row.total
    completed_tasks = row.completed
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    progress = await _get_progress(db, user.id)
    pillar_scores = _extract_pillar_scores(progress)
    pillar_movements = _build_pillar_movements(pillar_scores)

    stage = stage_for_day(start_day)
    coaching_note = _select_coaching_paragraph(
        stage, completion_rate, pillar_scores
    )
    focus_next_week = _select_focus_paragraph(stage, pillar_scores, week_number + 1)

    return {
        "week_number": week_number,
        "season": user.season,
        "completion_rate": round(completion_rate, 1),
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "pillar_movements": pillar_movements,
        "coaching_note": coaching_note,
        "focus_next_week": focus_next_week,
        "generated_at": None,
    }


async def get_weekly_reports_list(
    db: AsyncSession,
    user: User,
) -> list[dict]:
    """Get all available weekly report summaries for the user."""
    current_week = (user.program_day - 1) // 7 + 1
    reports = []
    for week in range(1, current_week + 1):
        start_day = (week - 1) * 7 + 1
        end_day = week * 7
        result = await db.execute(
            select(
                func.count().label("total"),
                func.count(DailyTask.completed_at).label("completed"),
            )
            .where(
                DailyTask.user_id == user.id,
                DailyTask.day_number >= start_day,
                DailyTask.day_number <= end_day,
            )
        )
        row = result.one()
        rate = (row.completed / row.total * 100) if row.total > 0 else 0.0
        reports.append({
            "week_number": week,
            "season": user.season,
            "completion_rate": round(rate, 1),
            "generated_at": None,
        })
    return reports


async def get_season_report(
    db: AsyncSession,
    user: User,
) -> dict:
    """Generate end-of-season narrative report from templates."""
    progress = await _get_progress(db, user.id)
    pillar_scores = _extract_pillar_scores(progress)

    result = await db.execute(
        select(
            func.count().label("total"),
            func.count(DailyTask.completed_at).label("completed"),
        )
        .where(DailyTask.user_id == user.id)
    )
    row = result.one()
    total_tasks = row.completed
    completion_rate = (row.completed / row.total * 100) if row.total > 0 else 0.0

    sorted_pillars = sorted(
        [(p, pillar_scores.get(p, 50)) for p in PILLARS],
        key=lambda x: x[1],
        reverse=True,
    )
    biggest_mover = sorted_pillars[0]
    weakest = sorted_pillars[-1]

    score_end = int(progress.optimisation_score) if progress else 50
    score_start = 50
    streak_best = progress.longest_streak if progress else 0

    variables = {
        "season": user.season,
        "next_season": user.season + 1,
        "biggest_mover_name": PILLAR_LABELS.get(biggest_mover[0], biggest_mover[0]),
        "biggest_mover_delta": biggest_mover[1] - 50,
        "biggest_mover_score": biggest_mover[1],
        "weakest_name": PILLAR_LABELS.get(weakest[0], weakest[0]),
        "weakest_score": weakest[1],
        "total_tasks_completed": total_tasks,
        "completion_rate": round(completion_rate, 1),
        "streak_best": streak_best,
        "score_start": score_start,
        "score_end": score_end,
        "score_delta": score_end - score_start,
    }

    idx = user.season % len(OPENING_PARAGRAPHS)
    opening = OPENING_PARAGRAPHS[idx].format(**variables)
    biggest_mover_text = BIGGEST_MOVER_PARAGRAPHS[idx % len(BIGGEST_MOVER_PARAGRAPHS)].format(**variables)
    needs_work = NEEDS_WORK_PARAGRAPHS[idx % len(NEEDS_WORK_PARAGRAPHS)].format(**variables)
    next_focus = NEXT_FOCUS_PARAGRAPHS[idx % len(NEXT_FOCUS_PARAGRAPHS)].format(**variables)

    return {
        "season": user.season,
        "opening": opening,
        "biggest_mover": biggest_mover_text,
        "needs_work": needs_work,
        "next_focus": next_focus,
        "score_start": score_start,
        "score_end": score_end,
        "score_delta": score_end - score_start,
        "total_tasks_completed": total_tasks,
        "completion_rate": round(completion_rate, 1),
        "streak_best": streak_best,
    }


def _determine_context(
    progress: Progress | None,
    program_day: int,
) -> tuple[str, str | None, dict]:
    """Determine the most relevant context for daily insight selection."""
    if progress is None:
        return "completion_rate", None, {
            "rate": 0, "day": program_day, "streak": 0,
            "pillar_name": "", "score": 50, "delta": 0,
        }

    streak_milestones = [7, 14, 30, 60, 90]
    if progress.current_streak in streak_milestones:
        return "streak_milestone", None, {
            "streak": progress.current_streak,
            "rate": 0,
            "day": program_day,
            "pillar_name": "",
            "score": 50,
            "delta": 0,
        }

    pillar_scores = _extract_pillar_scores(progress)
    biggest_mover = None
    biggest_delta = 0
    for pillar, score in pillar_scores.items():
        delta = score - 50
        if abs(delta) > abs(biggest_delta):
            biggest_delta = delta
            biggest_mover = pillar

    if biggest_mover and biggest_delta > 0:
        context_type = "pillar_up"
        return context_type, biggest_mover, {
            "pillar_name": PILLAR_LABELS.get(biggest_mover, biggest_mover),
            "score": pillar_scores[biggest_mover],
            "delta": abs(biggest_delta),
            "streak": progress.current_streak,
            "rate": 0,
            "day": program_day,
        }

    if biggest_mover and biggest_delta < 0:
        context_type = "pillar_down"
        return context_type, None, {
            "pillar_name": PILLAR_LABELS.get(biggest_mover, biggest_mover),
            "score": pillar_scores[biggest_mover],
            "delta": abs(biggest_delta),
            "streak": progress.current_streak,
            "rate": 0,
            "day": program_day,
        }

    return "completion_rate", None, {
        "rate": 0, "day": program_day, "streak": progress.current_streak,
        "pillar_name": "", "score": 50, "delta": 0,
    }


def _select_coaching_paragraph(
    stage: str,
    completion_rate: float,
    pillar_scores: dict[str, int],
) -> str:
    """Select coaching paragraph based on stage and completion context."""
    if completion_rate >= 70:
        context = "high_completion"
    elif completion_rate < 50:
        context = "low_completion"
    else:
        context = "pillar_weakness"

    weakest = min(pillar_scores.items(), key=lambda x: x[1])
    variables = {
        "rate": round(completion_rate, 1),
        "pillar_name": PILLAR_LABELS.get(weakest[0], weakest[0]),
        "score": weakest[1],
        "week": 0,
        "streak": 0,
    }

    templates = COACHING_PARAGRAPHS.get((stage, context), [])
    if not templates:
        templates = COACHING_PARAGRAPHS.get(("outcome", "high_completion"), [])
    if not templates:
        return "Keep up the consistent effort across all pillars."

    idx = int(completion_rate) % len(templates)
    return templates[idx].format(**variables)


def _select_focus_paragraph(
    stage: str,
    pillar_scores: dict[str, int],
    next_week: int,
) -> str:
    """Select focus paragraph for next week."""
    weakest = min(pillar_scores.items(), key=lambda x: x[1])
    variables = {
        "week": next_week,
        "pillar_name": PILLAR_LABELS.get(weakest[0], weakest[0]),
        "score": weakest[1],
    }

    templates = FOCUS_PARAGRAPHS.get((stage, "pillar_focus"), [])
    if not templates:
        templates = FOCUS_PARAGRAPHS.get((stage, "general"), [])
    if not templates:
        return f"Focus on consistency in week {next_week}."

    idx = next_week % len(templates)
    return templates[idx].format(**variables)


def _extract_pillar_scores(progress: Progress | None) -> dict[str, int]:
    """Extract pillar scores as a simple dict."""
    if progress is None:
        return {p: 50 for p in PILLARS}
    scores = {}
    for pillar, field in PILLAR_DB_FIELDS.items():
        scores[pillar] = getattr(progress, field, 50)
    return scores


def _build_pillar_movements(pillar_scores: dict[str, int]) -> list[dict]:
    """Build pillar movement list for weekly report."""
    movements = []
    for pillar in PILLARS:
        score = pillar_scores.get(pillar, 50)
        movements.append({
            "pillar": pillar,
            "label": PILLAR_LABELS.get(pillar, pillar),
            "score": score,
            "delta": score - 50,
        })
    return sorted(movements, key=lambda x: x["score"], reverse=True)


async def _get_progress(db: AsyncSession, user_id: uuid.UUID) -> Progress | None:
    """Fetch progress row."""
    result = await db.execute(
        select(Progress).where(Progress.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _get_stored_report(
    db: AsyncSession,
    user_id: uuid.UUID,
    week_number: int,
    season: int,
) -> dict | None:
    """Check for a pre-generated weekly report in the DB."""
    result = await db.execute(
        select(WeeklyReport).where(
            WeeklyReport.user_id == user_id,
            WeeklyReport.week_number == week_number,
            WeeklyReport.season == season,
        )
    )
    report = result.scalar_one_or_none()
    if report is None:
        return None
    return report.content


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Coaching service orchestrating template-based insight generation.
Zero LLM calls — all content deterministic from templates + user data.

Flow:
1. get_daily_insight() — determine context (streak, pillar mover, rate) → select template → interpolate
2. get_weekly_report() — aggregate week's tasks → select coaching/focus paragraphs → build report
3. get_season_report() — compile season stats → fill narrative templates

Main Entry Point: get_daily_insight, get_weekly_report, get_season_report

Dependencies:
- src.coaching.language_stage: stage_for_day
- src.coaching.templates: DAILY_INSIGHT_TEMPLATES
- src.coaching.weekly_templates: COACHING_PARAGRAPHS, FOCUS_PARAGRAPHS
- src.coaching.season_templates: narrative templates
- src.database.models: Progress, DailyTask, WeeklyReport, User
"""
