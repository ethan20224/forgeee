"""Tests for gamification: badges, challenges, XP/levels, streak milestones."""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Achievement, ChallengeProgress, Progress
from src.gamification.badges import BADGE_CATALOG, get_badges_for_condition
from src.gamification.xp import calculate_level, get_level_name, xp_for_next_level

SIGNUP_URL = "/api/v1/auth/signup"
ACHIEVEMENTS_URL = "/api/v1/gamification/achievements"
CHALLENGES_URL = "/api/v1/gamification/challenges"
START_CHALLENGE_URL = "/api/v1/gamification/challenges/start"
STREAK_URL = "/api/v1/gamification/streak"
XP_URL = "/api/v1/gamification/xp"


async def _create_user(client: AsyncClient, db_session: AsyncSession) -> tuple[dict, uuid.UUID]:
    """Helper: sign up and return tokens + user_id."""
    email = f"gam-test-{uuid.uuid4().hex[:8]}@forge.app"
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Gam Tester"},
    )
    assert resp.status_code == 201
    tokens = resp.json()

    from src.database.models import User

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    return tokens, user.id


def _auth(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# ---------------------------------------------------------------------------
# Unit Tests — XP/Level Calculation
# ---------------------------------------------------------------------------


class TestXPCalculation:
    def test_level_1_at_zero_xp(self):
        assert calculate_level(0) == 1

    def test_level_2_at_100_xp(self):
        assert calculate_level(100) == 2

    def test_level_5_at_800_xp(self):
        assert calculate_level(800) == 5

    def test_level_10_at_3800_xp(self):
        assert calculate_level(3800) == 10

    def test_level_25_max(self):
        assert calculate_level(100000) == 25

    def test_level_names(self):
        assert get_level_name(1) == "Beginner"
        assert get_level_name(10) == "Established"
        assert get_level_name(25) == "FORGE"

    def test_xp_for_next_level_progress(self):
        info = xp_for_next_level(150)
        assert info["current_level"] == 2
        assert info["xp_progress"] == 50
        assert info["xp_needed"] == 150
        assert info["progress_pct"] == pytest.approx(33.3, abs=0.1)

    def test_xp_for_next_level_max(self):
        info = xp_for_next_level(50000)
        assert info["current_level"] == 25
        assert info["progress_pct"] == 100.0
        assert info["xp_for_next_level"] is None


# ---------------------------------------------------------------------------
# Unit Tests — Badge Conditions
# ---------------------------------------------------------------------------


class TestBadgeConditions:
    def test_streak_3_unlocks_at_3(self):
        badges = get_badges_for_condition("streak", 3)
        ids = [b.badge_id for b in badges]
        assert "streak_3" in ids

    def test_streak_7_not_at_5(self):
        badges = get_badges_for_condition("streak", 5)
        ids = [b.badge_id for b in badges]
        assert "streak_7" not in ids
        assert "streak_3" in ids

    def test_multiple_badges_at_high_streak(self):
        badges = get_badges_for_condition("streak", 30)
        ids = [b.badge_id for b in badges]
        assert "streak_3" in ids
        assert "streak_7" in ids
        assert "streak_14" in ids
        assert "streak_30" in ids
        assert "streak_60" not in ids

    def test_tasks_completed_badges(self):
        badges = get_badges_for_condition("tasks_completed", 100)
        ids = [b.badge_id for b in badges]
        assert "tasks_10" in ids
        assert "tasks_50" in ids
        assert "tasks_100" in ids
        assert "tasks_250" not in ids

    def test_no_badges_for_unknown_condition(self):
        badges = get_badges_for_condition("unknown", 999)
        assert badges == []


# ---------------------------------------------------------------------------
# Integration Tests — Achievements Endpoint
# ---------------------------------------------------------------------------


class TestAchievementsEndpoint:
    @pytest.mark.asyncio
    async def test_returns_all_badges(self, client: AsyncClient, db_session: AsyncSession):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.get(ACHIEVEMENTS_URL, headers=_auth(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_available"] == len(BADGE_CATALOG)
        assert data["total_unlocked"] == 0

    @pytest.mark.asyncio
    async def test_shows_unlocked_badges(self, client: AsyncClient, db_session: AsyncSession):
        tokens, user_id = await _create_user(client, db_session)

        achievement = Achievement(
            user_id=user_id,
            badge_id="streak_3",
            unlocked_at=datetime.now(UTC),
        )
        db_session.add(achievement)
        await db_session.flush()

        resp = await client.get(ACHIEVEMENTS_URL, headers=_auth(tokens))
        data = resp.json()
        assert data["total_unlocked"] == 1
        streak3 = next(b for b in data["badges"] if b["badge_id"] == "streak_3")
        assert streak3["unlocked"] is True

    @pytest.mark.asyncio
    async def test_badge_unlock_is_idempotent(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user_id = await _create_user(client, db_session)

        from src.gamification.service import unlock_badges_for_event

        newly1 = await unlock_badges_for_event(user_id, "streak", 3, db_session)
        assert "streak_3" in newly1

        newly2 = await unlock_badges_for_event(user_id, "streak", 3, db_session)
        assert newly2 == []


# ---------------------------------------------------------------------------
# Integration Tests — Challenges Endpoint
# ---------------------------------------------------------------------------


class TestChallengesEndpoint:
    @pytest.mark.asyncio
    async def test_lists_available_challenges(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.get(CHALLENGES_URL, headers=_auth(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["available"]) > 0
        assert data["completed_count"] == 0

    @pytest.mark.asyncio
    async def test_start_challenge(self, client: AsyncClient, db_session: AsyncSession):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.post(
            START_CHALLENGE_URL,
            json={"challenge_id": "streak_7_challenge"},
            headers=_auth(tokens),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["challenge_id"] == "streak_7_challenge"
        assert data["status"] == "active"
        assert data["progress"] == 0

    @pytest.mark.asyncio
    async def test_start_duplicate_challenge_fails(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, _ = await _create_user(client, db_session)
        await client.post(
            START_CHALLENGE_URL,
            json={"challenge_id": "streak_7_challenge"},
            headers=_auth(tokens),
        )
        resp = await client.post(
            START_CHALLENGE_URL,
            json={"challenge_id": "streak_7_challenge"},
            headers=_auth(tokens),
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_start_nonexistent_challenge(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.post(
            START_CHALLENGE_URL,
            json={"challenge_id": "does_not_exist"},
            headers=_auth(tokens),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_challenge_progress_update(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user_id = await _create_user(client, db_session)

        cp = ChallengeProgress(
            user_id=user_id,
            challenge_id="streak_7_challenge",
            status="active",
            progress=5,
            target=7,
            started_at=datetime.now(UTC),
        )
        db_session.add(cp)
        await db_session.flush()

        from src.gamification.service import update_challenge_progress

        completed = await update_challenge_progress(
            user_id, "streak_7_challenge", 2, db_session
        )
        assert completed is True
        assert cp.status == "completed"
        assert cp.progress == 7


# ---------------------------------------------------------------------------
# Integration Tests — Streak & XP Endpoints
# ---------------------------------------------------------------------------


class TestStreakEndpoint:
    @pytest.mark.asyncio
    async def test_returns_streak_info(self, client: AsyncClient, db_session: AsyncSession):
        tokens, user_id = await _create_user(client, db_session)

        result = await db_session.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one()
        progress.current_streak = 10
        progress.longest_streak = 15
        await db_session.flush()

        resp = await client.get(STREAK_URL, headers=_auth(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_streak"] == 10
        assert data["longest_streak"] == 15
        assert data["next_milestone"] == 14

    @pytest.mark.asyncio
    async def test_streak_milestones_list(self, client: AsyncClient, db_session: AsyncSession):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.get(STREAK_URL, headers=_auth(tokens))
        data = resp.json()
        assert data["milestones"] == [3, 7, 14, 30, 60, 90]


class TestXPEndpoint:
    @pytest.mark.asyncio
    async def test_returns_xp_info(self, client: AsyncClient, db_session: AsyncSession):
        tokens, user_id = await _create_user(client, db_session)

        result = await db_session.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one()
        progress.total_xp = 500
        await db_session.flush()

        resp = await client.get(XP_URL, headers=_auth(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_xp"] == 500
        assert data["current_level"] == 4
        assert data["level_name"] == "Dedicated"

    @pytest.mark.asyncio
    async def test_new_user_level_1(self, client: AsyncClient, db_session: AsyncSession):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.get(XP_URL, headers=_auth(tokens))
        data = resp.json()
        assert data["current_level"] == 1
        assert data["level_name"] == "Beginner"
        assert data["total_xp"] == 0
