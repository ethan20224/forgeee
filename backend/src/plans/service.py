"""Plan generation service — DeepSeek V4-Flash + cache + persistence."""

import hashlib
import json
import logging
import re
import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import get_settings
from src.database.models import (
    DailyTask,
    Plan,
    PlanCache,
    QuizAnswer,
    TaskLibrarySelection,
)
from src.plans.prompts import SYSTEM_PROMPT, build_user_prompt
from src.plans.schemas import LLMPlanOutput
from src.plans.task_library import TASKS_BY_ID

logger = logging.getLogger(__name__)


def _quiz_hash(quiz: QuizAnswer) -> str:
    """Deterministic hash of quiz answers for cache lookup."""
    payload = json.dumps(
        {
            "goals": sorted(quiz.goals or []),
            "routine_level": quiz.routine_level,
            "daily_time": quiz.daily_time,
            "timeline": quiz.timeline,
            "main_concern": quiz.main_concern,
            "age_range": quiz.age_range,
            "has_photo": quiz.has_photo,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers from LLM output."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _build_mock_plan() -> dict:
    """Return a valid mock plan for AI_SIMULATION mode."""
    weeks = []
    day_counter = 1
    mock_tasks_by_day = [
        [
            {"library_task_id": "skin-b-01", "pillar": "skin", "tier": "beginner"},
            {"library_task_id": "hair-b-01", "pillar": "hair", "tier": "beginner"},
            {"library_task_id": "post-b-01", "pillar": "posture", "tier": "beginner"},
        ],
        [
            {"library_task_id": "groom-b-01", "pillar": "grooming", "tier": "beginner"},
            {"library_task_id": "style-b-01", "pillar": "style", "tier": "beginner"},
            {"library_task_id": "sleep-b-01", "pillar": "sleep", "tier": "beginner"},
        ],
        [
            {"library_task_id": "nutr-b-01", "pillar": "nutrition", "tier": "beginner"},
            {"library_task_id": "voice-b-01", "pillar": "voice", "tier": "beginner"},
            {"library_task_id": "face-b-01", "pillar": "facial_composition", "tier": "beginner"},
        ],
    ]

    for week_num in range(1, 14):
        days = []
        for _ in range(7):
            tasks = mock_tasks_by_day[(day_counter - 1) % 3]
            days.append({"day": day_counter, "tasks": tasks})
            day_counter += 1
        weeks.append({"week": week_num, "days": days})

    return {
        "program_name": "Foundation Builder (Mock)",
        "focus_summary": "A simulated 90-day plan for development testing.",
        "honest_expectation": "This is mock data. Real plans use DeepSeek AI.",
        "weeks": weeks,
    }


async def _call_deepseek(quiz: QuizAnswer) -> dict:
    """Call DeepSeek V4-Flash API and return parsed JSON plan."""
    settings = get_settings()

    user_prompt = build_user_prompt(
        goals=quiz.goals or [],
        routine_level=quiz.routine_level or "none",
        daily_time=quiz.daily_time or "20min",
        timeline=quiz.timeline or "90days",
        main_concern=quiz.main_concern or "overall",
        age_range=quiz.age_range or "25-29",
        has_photo=quiz.has_photo,
    )

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{settings.deepseek_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.deepseek_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 16000,
            },
        )
        resp.raise_for_status()

    data = resp.json()
    raw_content = data["choices"][0]["message"]["content"]
    clean = _strip_markdown_fences(raw_content)
    return json.loads(clean)


def validate_plan(raw: dict) -> LLMPlanOutput:
    """Validate and parse the LLM output against our schema.

    Raises:
        ValidationError: If the plan structure is invalid.
        ValueError: If business rules are violated.
    """
    plan = LLMPlanOutput.model_validate(raw)

    if len(plan.weeks) != 13:
        raise ValueError(f"Expected 13 weeks, got {len(plan.weeks)}")

    total_days = sum(len(w.days) for w in plan.weeks)
    if total_days < 90:
        raise ValueError(f"Expected >=90 days, got {total_days}")

    for week in plan.weeks:
        for day in week.days:
            for task in day.tasks:
                if task.library_task_id not in TASKS_BY_ID:
                    raise ValueError(f"Unknown task ID: {task.library_task_id}")

    return plan


def _persist_plan(
    db_plan: Plan,
    validated: LLMPlanOutput,
    user_id: uuid.UUID,
) -> tuple[list[DailyTask], list[TaskLibrarySelection]]:
    """Build DailyTask and TaskLibrarySelection rows from validated plan."""
    daily_tasks: list[DailyTask] = []
    seen_library_ids: dict[str, int] = {}

    for week in validated.weeks:
        for day in week.days:
            for task_spec in day.tasks:
                lib_task = TASKS_BY_ID.get(task_spec.library_task_id)
                dt = DailyTask(
                    user_id=user_id,
                    plan_id=db_plan.id,
                    title=lib_task.title if lib_task else task_spec.library_task_id,
                    category=task_spec.pillar,
                    pillar=task_spec.pillar,
                    tier=task_spec.tier,
                    why_it_works=lib_task.why_it_works if lib_task else None,
                    duration_mins=lib_task.duration_mins if lib_task else None,
                    day_number=day.day,
                    week_number=week.week,
                    xp_value=lib_task.xp_value if lib_task else 10,
                    library_task_id=task_spec.library_task_id,
                )
                daily_tasks.append(dt)

                seen_library_ids[task_spec.library_task_id] = (
                    seen_library_ids.get(task_spec.library_task_id, 0) + 1
                )

    selections = [
        TaskLibrarySelection(
            user_id=user_id,
            plan_id=db_plan.id,
            library_task_id=lid,
            used_count=count,
        )
        for lid, count in seen_library_ids.items()
    ]

    return daily_tasks, selections


async def generate_plan(
    db: AsyncSession,
    user_id: uuid.UUID,
    quiz: QuizAnswer,
    season: int = 1,
) -> tuple[Plan, bool]:
    """Generate (or retrieve cached) plan. Returns (plan, from_cache)."""
    settings = get_settings()
    q_hash = _quiz_hash(quiz)

    # Check cache
    cache_result = await db.execute(select(PlanCache).where(PlanCache.quiz_hash == q_hash))
    cached = cache_result.scalar_one_or_none()

    if cached is not None:
        raw_plan = cached.plan_json
        cached.hit_count += 1
        from_cache = True
    else:
        if settings.ai_simulation:
            raw_plan = _build_mock_plan()
        else:
            raw_plan = await _call_deepseek(quiz)
        from_cache = False

    validated = validate_plan(raw_plan)

    db_plan = Plan(
        user_id=user_id,
        season=season,
        program_name=validated.program_name,
        focus_summary=validated.focus_summary,
        honest_expectation=validated.honest_expectation,
        raw_json=raw_plan,
    )
    db.add(db_plan)
    await db.flush()

    daily_tasks, selections = _persist_plan(db_plan, validated, user_id)
    db.add_all(daily_tasks)
    db.add_all(selections)

    if not from_cache:
        cache_entry = PlanCache(quiz_hash=q_hash, plan_json=raw_plan)
        db.add(cache_entry)

    await db.flush()
    await db.refresh(db_plan, ["daily_tasks"])

    return db_plan, from_cache


async def get_current_plan(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Plan | None:
    """Get the user's latest plan with tasks eagerly loaded."""
    result = await db.execute(
        select(Plan)
        .where(Plan.user_id == user_id)
        .options(selectinload(Plan.daily_tasks))
        .order_by(Plan.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_plan_by_id(
    db: AsyncSession,
    plan_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Plan | None:
    """Get a specific plan by ID, scoped to the user."""
    result = await db.execute(
        select(Plan)
        .where(Plan.id == plan_id, Plan.user_id == user_id)
        .options(selectinload(Plan.daily_tasks))
    )
    return result.scalar_one_or_none()
