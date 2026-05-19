import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DailyTask, Plan, Progress, User
from src.tasks.service import (
    DRIFT_PER_TASK,
    MAX_PILLAR_SCORE,
    STREAK_BONUS_THRESHOLD,
    STREAK_BONUS_XP,
    XP_PER_TASK,
    level_from_xp,
)

SIGNUP_URL = "/api/v1/auth/signup"
TODAY_URL = "/api/v1/tasks/today"
COMPLETE_URL = "/api/v1/tasks/{task_id}/complete"
HEATMAP_URL = "/api/v1/tasks/heatmap"


async def _create_user_with_tasks(
    client: AsyncClient,
    db_session: AsyncSession,
    program_day: int = 1,
    num_tasks: int = 3,
    pillar: str = "skin",
) -> tuple[dict, list[DailyTask]]:
    """Helper: create a signed-up user and seed tasks for their program_day."""
    resp = await client.post(
        SIGNUP_URL,
        json={
            "email": f"task-test-{uuid.uuid4().hex[:8]}@forge.app",
            "password": "securepass123",
            "name": "Task Tester",
        },
    )
    assert resp.status_code == 201
    tokens = resp.json()

    from sqlalchemy import select

    result = await db_session.execute(
        select(User).where(User.email.like("task-test-%"))
        .order_by(User.created_at.desc())
    )
    user = result.scalars().first()
    user.program_day = program_day

    plan = Plan(user_id=user.id, season=1, program_name="Test Plan")
    db_session.add(plan)
    await db_session.flush()

    tasks = []
    for i in range(num_tasks):
        task = DailyTask(
            user_id=user.id,
            plan_id=plan.id,
            title=f"Test Task {i + 1}",
            category="daily",
            pillar=pillar,
            tier="beginner",
            day_number=program_day,
            xp_value=XP_PER_TASK,
            week_number=1,
        )
        db_session.add(task)
        tasks.append(task)

    await db_session.flush()
    return tokens, tasks


@pytest.mark.asyncio
async def test_get_todays_tasks(client, db_session):
    """GET /today returns tasks for the user's current program_day."""
    tokens, tasks = await _create_user_with_tasks(client, db_session, program_day=5)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(TODAY_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert all(t["day_number"] == 5 for t in data)
    assert all(t["is_completed"] is False for t in data)


@pytest.mark.asyncio
async def test_get_todays_tasks_empty(client, db_session):
    """GET /today returns empty list when no tasks exist for program_day."""
    tokens, _ = await _create_user_with_tasks(client, db_session, program_day=5)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from sqlalchemy import select

    result = await db_session.execute(
        select(User).where(User.email.like("task-test-%"))
        .order_by(User.created_at.desc())
    )
    user = result.scalars().first()
    user.program_day = 99
    await db_session.flush()

    resp = await client.get(TODAY_URL, headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_complete_task(client, db_session):
    """POST /{task_id}/complete marks task done and returns XP details."""
    tokens, tasks = await _create_user_with_tasks(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    task_id = str(tasks[0].id)

    resp = await client.post(COMPLETE_URL.format(task_id=task_id), headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["task_id"] == task_id
    assert data["xp_earned"] == XP_PER_TASK
    assert data["streak_bonus"] == 0
    assert data["total_xp"] == XP_PER_TASK
    assert data["new_streak"] == 1
    assert data["pillar_affected"] == "skin"


@pytest.mark.asyncio
async def test_xp_award_accumulates(client, db_session):
    """Completing multiple tasks accumulates XP."""
    tokens, tasks = await _create_user_with_tasks(client, db_session, num_tasks=3)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    for i, task in enumerate(tasks):
        resp = await client.post(
            COMPLETE_URL.format(task_id=str(task.id)), headers=headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_xp"] == XP_PER_TASK * (i + 1)


@pytest.mark.asyncio
async def test_streak_increment(client, db_session):
    """Streak increments when tasks completed on consecutive days."""
    tokens, tasks = await _create_user_with_tasks(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from sqlalchemy import select

    result = await db_session.execute(
        select(Progress).join(User).where(User.email.like("task-test-%"))
        .order_by(User.created_at.desc())
    )
    progress = result.scalars().first()
    progress.current_streak = 3
    progress.longest_streak = 3
    progress.last_active_date = date.today() - timedelta(days=1)
    await db_session.flush()

    resp = await client.post(
        COMPLETE_URL.format(task_id=str(tasks[0].id)), headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_streak"] == 4


@pytest.mark.asyncio
async def test_streak_bonus_xp(client, db_session):
    """Streak bonus (+5 XP) awarded when streak > 3."""
    tokens, tasks = await _create_user_with_tasks(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from sqlalchemy import select

    result = await db_session.execute(
        select(Progress).join(User).where(User.email.like("task-test-%"))
        .order_by(User.created_at.desc())
    )
    progress = result.scalars().first()
    progress.current_streak = STREAK_BONUS_THRESHOLD + 1
    progress.longest_streak = STREAK_BONUS_THRESHOLD + 1
    progress.last_active_date = date.today() - timedelta(days=1)
    await db_session.flush()

    resp = await client.post(
        COMPLETE_URL.format(task_id=str(tasks[0].id)), headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["streak_bonus"] == STREAK_BONUS_XP
    assert data["xp_earned"] == XP_PER_TASK + STREAK_BONUS_XP


@pytest.mark.asyncio
async def test_streak_reset_after_gap(client, db_session):
    """Streak resets to 1 when more than 1 day gap."""
    tokens, tasks = await _create_user_with_tasks(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from sqlalchemy import select

    result = await db_session.execute(
        select(Progress).join(User).where(User.email.like("task-test-%"))
        .order_by(User.created_at.desc())
    )
    progress = result.scalars().first()
    progress.current_streak = 10
    progress.longest_streak = 10
    progress.last_active_date = date.today() - timedelta(days=3)
    await db_session.flush()

    resp = await client.post(
        COMPLETE_URL.format(task_id=str(tasks[0].id)), headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_streak"] == 1


@pytest.mark.asyncio
async def test_drift_cap_at_100(client, db_session):
    """Score drift is capped at 100 (MAX_PILLAR_SCORE)."""
    tokens, tasks = await _create_user_with_tasks(client, db_session, pillar="skin")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from sqlalchemy import select

    result = await db_session.execute(
        select(Progress).join(User).where(User.email.like("task-test-%"))
        .order_by(User.created_at.desc())
    )
    progress = result.scalars().first()
    progress.skin_score = 100
    await db_session.flush()

    resp = await client.post(
        COMPLETE_URL.format(task_id=str(tasks[0].id)), headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_pillar_score"] == MAX_PILLAR_SCORE


@pytest.mark.asyncio
async def test_idempotency_no_double_xp(client, db_session):
    """Completing the same task twice doesn't award XP twice."""
    tokens, tasks = await _create_user_with_tasks(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    task_id = str(tasks[0].id)

    resp1 = await client.post(COMPLETE_URL.format(task_id=task_id), headers=headers)
    assert resp1.status_code == 200
    first_xp = resp1.json()["total_xp"]

    resp2 = await client.post(COMPLETE_URL.format(task_id=task_id), headers=headers)
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["xp_earned"] == 0
    assert data["streak_bonus"] == 0


@pytest.mark.asyncio
async def test_complete_nonexistent_task(client, db_session):
    """Completing a non-existent task returns 404."""
    tokens, _ = await _create_user_with_tasks(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    fake_id = str(uuid.uuid4())

    resp = await client.post(COMPLETE_URL.format(task_id=fake_id), headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_heatmap_returns_data(client, db_session):
    """GET /heatmap returns completion data grouped by day."""
    tokens, tasks = await _create_user_with_tasks(client, db_session, num_tasks=3)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    await client.post(
        COMPLETE_URL.format(task_id=str(tasks[0].id)), headers=headers
    )

    resp = await client.get(HEATMAP_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_days"] == 1
    assert data["days"][0]["total_tasks"] == 3
    assert data["days"][0]["completed_tasks"] == 1
    assert data["overall_completion_rate"] == pytest.approx(33.3, abs=0.1)


@pytest.mark.asyncio
async def test_heatmap_empty(client, db_session):
    """GET /heatmap returns empty when no tasks exist."""
    resp = await client.post(
        SIGNUP_URL,
        json={
            "email": f"heatmap-empty-{uuid.uuid4().hex[:8]}@forge.app",
            "password": "securepass123",
        },
    )
    tokens = resp.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(HEATMAP_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_days"] == 0
    assert data["days"] == []
    assert data["overall_completion_rate"] == 0.0


@pytest.mark.asyncio
async def test_level_calculation():
    """Level is correctly derived from XP thresholds."""
    assert level_from_xp(0) == 1
    assert level_from_xp(99) == 1
    assert level_from_xp(100) == 2
    assert level_from_xp(249) == 2
    assert level_from_xp(250) == 3
    assert level_from_xp(500) == 4
    assert level_from_xp(50000) == 20


@pytest.mark.asyncio
async def test_score_drift_applies_to_correct_pillar(client, db_session):
    """Drift applies specifically to the task's pillar, not others."""
    tokens, tasks = await _create_user_with_tasks(
        client, db_session, pillar="hair"
    )
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.post(
        COMPLETE_URL.format(task_id=str(tasks[0].id)), headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pillar_affected"] == "hair"
    assert data["new_pillar_score"] == 50


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Integration tests for the task engine (P6).

Flow:
1. Helper creates authenticated user + seeded DailyTask rows
2. Tests exercise GET /today, POST /complete, GET /heatmap
3. Verifies XP, streak, drift, idempotency, and edge cases

Main Entry Point: pytest (run with `pytest src/tasks/tests/`)

Dependencies:
- conftest.py: test DB, client fixture, transaction rollback
- src.tasks: module under test
"""
