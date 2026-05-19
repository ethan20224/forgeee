"""Integration tests for progress endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DailyTask, Plan, Progress, User

SIGNUP_URL = "/api/v1/auth/signup"
PROGRESS_URL = "/api/v1/progress/"
PILLAR_URL = "/api/v1/progress/pillar/{pillar}"


async def _create_user(client: AsyncClient, db_session: AsyncSession) -> tuple[dict, User]:
    """Helper: create a user and return tokens + user object."""
    email = f"progress-{uuid.uuid4().hex[:8]}@forge.app"
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Progress Tester"},
    )
    assert resp.status_code == 201
    tokens = resp.json()

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    return tokens, user


@pytest.mark.asyncio
async def test_get_progress_default_scores(client, db_session):
    """GET /progress/ returns default 50 scores for new user."""
    tokens, _ = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(PROGRESS_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_streak"] == 0
    assert data["total_xp"] == 0
    assert data["level"] == 1
    assert len(data["pillar_scores"]) == 9
    for ps in data["pillar_scores"]:
        assert ps["score"] == 50
        assert ps["delta_vs_baseline"] == 0


@pytest.mark.asyncio
async def test_get_progress_reflects_updated_scores(client, db_session):
    """GET /progress/ reflects updated pillar scores."""
    tokens, user = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    result = await db_session.execute(
        select(Progress).where(Progress.user_id == user.id)
    )
    progress = result.scalar_one()
    progress.skin_score = 75
    progress.total_xp = 200
    progress.current_streak = 5
    await db_session.flush()

    resp = await client.get(PROGRESS_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_xp"] == 200
    assert data["current_streak"] == 5

    skin = next(p for p in data["pillar_scores"] if p["pillar"] == "skin")
    assert skin["score"] == 75
    assert skin["delta_vs_baseline"] == 25


@pytest.mark.asyncio
async def test_get_progress_voice_excluded_season_1(client, db_session):
    """Voice pillar has weight 0 in Season 1."""
    tokens, _ = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(PROGRESS_URL, headers=headers)
    data = resp.json()
    voice = next(p for p in data["pillar_scores"] if p["pillar"] == "voice")
    assert voice["weight"] == 0.0


@pytest.mark.asyncio
async def test_get_progress_voice_included_season_2(client, db_session):
    """Voice pillar has positive weight in Season 2."""
    tokens, user = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    user.season = 2
    await db_session.flush()

    resp = await client.get(PROGRESS_URL, headers=headers)
    data = resp.json()
    voice = next(p for p in data["pillar_scores"] if p["pillar"] == "voice")
    assert voice["weight"] > 0


@pytest.mark.asyncio
async def test_pillar_detail_valid_pillar(client, db_session):
    """GET /pillar/{pillar} returns detail for a valid pillar."""
    tokens, user = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(
        PILLAR_URL.format(pillar="skin"), headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pillar"] == "skin"
    assert data["label"] == "Skin"
    assert data["score"] == 50
    assert data["rank"] >= 1
    assert data["tasks_completed"] == 0
    assert data["history"] == []


@pytest.mark.asyncio
async def test_pillar_detail_invalid_pillar(client, db_session):
    """GET /pillar/{pillar} returns 404 for invalid pillar."""
    tokens, _ = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(
        PILLAR_URL.format(pillar="nonexistent"), headers=headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_pillar_detail_with_completed_tasks(client, db_session):
    """Pillar detail shows completed task count and history."""
    tokens, user = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    plan = Plan(user_id=user.id, season=1, program_name="Test")
    db_session.add(plan)
    await db_session.flush()

    for day in [1, 2, 3]:
        task = DailyTask(
            user_id=user.id,
            plan_id=plan.id,
            title=f"Skin Task Day {day}",
            category="daily",
            pillar="skin",
            tier="beginner",
            day_number=day,
            is_completed=True,
            week_number=1,
        )
        db_session.add(task)
    await db_session.flush()

    resp = await client.get(
        PILLAR_URL.format(pillar="skin"), headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tasks_completed"] == 3
    assert len(data["history"]) == 3
    assert data["history"][0]["day_number"] == 1


@pytest.mark.asyncio
async def test_progress_requires_auth(client):
    """Progress endpoints require authentication."""
    resp = await client.get(PROGRESS_URL)
    assert resp.status_code in (401, 403)


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Integration tests for the progress API endpoints (P7).

Flow:
1. Helper creates authenticated user
2. Tests exercise GET /progress/ and GET /pillar/{pillar}
3. Verifies default scores, updated scores, seasonal reweight, auth guard

Main Entry Point: pytest (run with `pytest src/progress/tests/`)

Dependencies:
- conftest.py: test DB, client fixture, transaction rollback
- src.progress: module under test
"""
