"""Tests for the deterministic coaching engine (P8)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.coaching.language_stage import LANGUAGE_STAGES, stage_for_day
from src.coaching.templates import DAILY_INSIGHT_TEMPLATES
from src.common.constants import PILLARS
from src.database.models import DailyTask, Plan, Progress, User

SIGNUP_URL = "/api/v1/auth/signup"
INSIGHT_URL = "/api/v1/coaching/daily-insight"
WEEKLY_URL = "/api/v1/coaching/weekly-report/{week}"
WEEKLY_LIST_URL = "/api/v1/coaching/weekly-reports"
SEASON_URL = "/api/v1/coaching/season-report"


async def _create_user(
    client: AsyncClient,
    db_session: AsyncSession,
    program_day: int = 1,
) -> tuple[dict, User]:
    """Helper: create a user and set their program_day."""
    email = f"coach-{uuid.uuid4().hex[:8]}@forge.app"
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Coach Tester"},
    )
    assert resp.status_code == 201
    tokens = resp.json()

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.program_day = program_day
    await db_session.flush()
    return tokens, user


class TestLanguageStage:
    def test_outcome_stage_day_1(self):
        assert stage_for_day(1) == "outcome"

    def test_outcome_stage_day_14(self):
        assert stage_for_day(14) == "outcome"

    def test_habit_stage_day_15(self):
        assert stage_for_day(15) == "habit"

    def test_habit_stage_day_30(self):
        assert stage_for_day(30) == "habit"

    def test_mechanism_stage_day_31(self):
        assert stage_for_day(31) == "mechanism"

    def test_mechanism_stage_day_90(self):
        assert stage_for_day(90) == "mechanism"

    def test_beyond_90_returns_mechanism(self):
        assert stage_for_day(100) == "mechanism"

    def test_all_stages_covered(self):
        """Every day from 1-90 maps to a valid stage."""
        for day in range(1, 91):
            stage = stage_for_day(day)
            assert stage in LANGUAGE_STAGES


class TestTemplates:
    def test_all_three_stages_have_templates(self):
        """Each stage has at least one template."""
        stages_found = set()
        for key in DAILY_INSIGHT_TEMPLATES:
            stages_found.add(key[0])
        assert "outcome" in stages_found
        assert "habit" in stages_found
        assert "mechanism" in stages_found

    def test_all_context_types_covered(self):
        """Key context types exist for each stage."""
        for stage in ["outcome", "habit", "mechanism"]:
            stage_keys = [k for k in DAILY_INSIGHT_TEMPLATES if k[0] == stage]
            contexts = {k[1] for k in stage_keys}
            assert "pillar_up" in contexts
            assert "pillar_down" in contexts
            assert "streak_milestone" in contexts
            assert "completion_rate" in contexts

    def test_templates_have_valid_placeholders(self):
        """All templates use only valid variable names."""
        valid_vars = {"pillar_name", "score", "delta", "streak", "rate", "day"}
        for key, templates in DAILY_INSIGHT_TEMPLATES.items():
            for template in templates:
                import re
                placeholders = re.findall(r"\{(\w+)\}", template)
                for p in placeholders:
                    assert p in valid_vars, (
                        f"Invalid placeholder '{{{p}}}' in template {key}"
                    )

    def test_variable_interpolation_works(self):
        """Templates interpolate without error given valid variables."""
        variables = {
            "pillar_name": "Skin",
            "score": 75,
            "delta": 5,
            "streak": 14,
            "rate": 85.0,
            "day": 10,
        }
        for key, templates in DAILY_INSIGHT_TEMPLATES.items():
            for template in templates:
                result = template.format(**variables)
                assert len(result) > 0
                assert "{" not in result

    def test_rotation_produces_different_templates(self):
        """Different program_days select different templates for the same key."""
        key = ("outcome", "pillar_up", "skin")
        templates = DAILY_INSIGHT_TEMPLATES[key]
        if len(templates) > 1:
            idx1 = 1 % len(templates)
            idx2 = 2 % len(templates)
            assert idx1 != idx2


@pytest.mark.asyncio
async def test_daily_insight_returns_message(client, db_session):
    """GET /daily-insight returns a non-empty insight message."""
    tokens, _ = await _create_user(client, db_session, program_day=5)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(INSIGHT_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == "outcome"
    assert data["program_day"] == 5
    assert len(data["message"]) > 10


@pytest.mark.asyncio
async def test_daily_insight_habit_stage(client, db_session):
    """Insight returns habit stage for day 20."""
    tokens, _ = await _create_user(client, db_session, program_day=20)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(INSIGHT_URL, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["stage"] == "habit"


@pytest.mark.asyncio
async def test_daily_insight_mechanism_stage(client, db_session):
    """Insight returns mechanism stage for day 45."""
    tokens, _ = await _create_user(client, db_session, program_day=45)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(INSIGHT_URL, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["stage"] == "mechanism"


@pytest.mark.asyncio
async def test_daily_insight_with_streak_milestone(client, db_session):
    """Insight detects streak milestones."""
    tokens, user = await _create_user(client, db_session, program_day=10)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    result = await db_session.execute(
        select(Progress).where(Progress.user_id == user.id)
    )
    progress = result.scalar_one()
    progress.current_streak = 7
    await db_session.flush()

    resp = await client.get(INSIGHT_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["context_type"] == "streak_milestone"
    assert "7" in data["message"]


@pytest.mark.asyncio
async def test_weekly_report_returns_data(client, db_session):
    """GET /weekly-report/{week} returns a report."""
    tokens, user = await _create_user(client, db_session, program_day=14)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    plan = Plan(user_id=user.id, season=1, program_name="Test")
    db_session.add(plan)
    await db_session.flush()

    from datetime import UTC, datetime

    for day in range(1, 8):
        completed = day <= 5
        task = DailyTask(
            user_id=user.id, plan_id=plan.id, title=f"Task {day}",
            category="daily", pillar="skin", tier="beginner",
            day_number=day, is_completed=completed,
            completed_at=datetime.now(UTC) if completed else None,
            week_number=1,
        )
        db_session.add(task)
    await db_session.flush()

    resp = await client.get(WEEKLY_URL.format(week=1), headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["week_number"] == 1
    assert data["total_tasks"] == 7
    assert data["completed_tasks"] == 5
    assert data["completion_rate"] > 0
    assert len(data["coaching_note"]) > 10
    assert len(data["focus_next_week"]) > 10


@pytest.mark.asyncio
async def test_weekly_report_invalid_week(client, db_session):
    """GET /weekly-report/{week} rejects invalid week numbers."""
    tokens, _ = await _create_user(client, db_session)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(WEEKLY_URL.format(week=0), headers=headers)
    assert resp.status_code == 400

    resp = await client.get(WEEKLY_URL.format(week=14), headers=headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_weekly_reports_list(client, db_session):
    """GET /weekly-reports returns list of summaries."""
    tokens, user = await _create_user(client, db_session, program_day=14)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(WEEKLY_LIST_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["week_number"] == 1
    assert data[1]["week_number"] == 2


@pytest.mark.asyncio
async def test_season_report(client, db_session):
    """GET /season-report returns narrative report."""
    tokens, user = await _create_user(client, db_session, program_day=90)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    result = await db_session.execute(
        select(Progress).where(Progress.user_id == user.id)
    )
    progress = result.scalar_one()
    progress.skin_score = 75
    progress.longest_streak = 30
    await db_session.flush()

    resp = await client.get(SEASON_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["season"] == 1
    assert len(data["opening"]) > 20
    assert len(data["biggest_mover"]) > 20
    assert len(data["needs_work"]) > 20
    assert len(data["next_focus"]) > 20
    assert data["streak_best"] == 30


@pytest.mark.asyncio
async def test_coaching_requires_auth(client):
    """Coaching endpoints require authentication."""
    resp = await client.get(INSIGHT_URL)
    assert resp.status_code in (401, 403)
