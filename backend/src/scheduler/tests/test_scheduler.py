"""Tests for scheduler background jobs."""

import uuid
from datetime import UTC, date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DailyTask, Plan, Progress, User, WeeklyReport
from src.scheduler.jobs import (
    advance_program_days,
    check_season_rollovers,
    check_streaks,
    generate_weekly_reports,
)

SIGNUP_URL = "/api/v1/auth/signup"


async def _create_onboarded_user(
    client: AsyncClient,
    db_session: AsyncSession,
    program_day: int = 1,
    last_active: date | None = None,
) -> User:
    email = f"sched-{uuid.uuid4().hex[:8]}@forge.app"
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Sched Tester"},
    )
    assert resp.status_code == 201

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.onboarded = True
    user.program_day = program_day
    user.last_active_date = last_active or (date.today() - timedelta(days=1))
    await db_session.flush()
    return user


class TestAdvanceProgramDays:
    @pytest.mark.asyncio
    async def test_advances_active_users(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        yesterday = date.today() - timedelta(days=1)
        user = await _create_onboarded_user(client, db_session, program_day=5, last_active=yesterday)

        count = await advance_program_days(db_session)
        assert count >= 1

        await db_session.refresh(user)
        assert user.program_day == 6

    @pytest.mark.asyncio
    async def test_does_not_advance_inactive_users(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        old_date = date.today() - timedelta(days=5)
        user = await _create_onboarded_user(client, db_session, program_day=10, last_active=old_date)

        await advance_program_days(db_session)

        await db_session.refresh(user)
        assert user.program_day == 10


class TestSeasonRollover:
    @pytest.mark.asyncio
    async def test_rolls_over_at_day_90(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        user = await _create_onboarded_user(client, db_session, program_day=90)

        count = await check_season_rollovers(db_session)
        assert count >= 1

        await db_session.refresh(user)
        assert user.season == 2
        assert user.program_day == 1

    @pytest.mark.asyncio
    async def test_does_not_roll_over_before_90(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        user = await _create_onboarded_user(client, db_session, program_day=89)

        count = await check_season_rollovers(db_session)

        await db_session.refresh(user)
        assert user.season == 1
        assert user.program_day == 89


class TestCheckStreaks:
    @pytest.mark.asyncio
    async def test_resets_stale_streaks(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        user = await _create_onboarded_user(client, db_session)

        result = await db_session.execute(select(Progress).where(Progress.user_id == user.id))
        progress = result.scalar_one()
        progress.current_streak = 5
        progress.last_active_date = date.today() - timedelta(days=3)
        await db_session.flush()

        count = await check_streaks(db_session)
        assert count >= 1

        await db_session.refresh(progress)
        assert progress.current_streak == 0

    @pytest.mark.asyncio
    async def test_preserves_active_streaks(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        user = await _create_onboarded_user(client, db_session)

        result = await db_session.execute(select(Progress).where(Progress.user_id == user.id))
        progress = result.scalar_one()
        progress.current_streak = 5
        progress.last_active_date = date.today()
        await db_session.flush()

        await check_streaks(db_session)

        await db_session.refresh(progress)
        assert progress.current_streak == 5


class TestWeeklyReports:
    @pytest.mark.asyncio
    async def test_generates_report(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        user = await _create_onboarded_user(client, db_session, program_day=8)

        plan = Plan(user_id=user.id, season=1, program_name="Test Plan")
        db_session.add(plan)
        await db_session.flush()

        for i in range(7):
            task = DailyTask(
                user_id=user.id,
                plan_id=plan.id,
                title=f"Task {i}",
                category="routine",
                pillar="skin",
                day_number=i + 1,
                is_completed=True,
                completed_at=datetime.now(UTC),
            )
            db_session.add(task)
        await db_session.flush()

        count = await generate_weekly_reports(db_session)
        assert count >= 1

        # week_number = (8-1)//7 + 1 = 2 — but tasks are for days 1-7 (week 1)
        # The function generates for the user's current week, so check week 2
        week_number = (user.program_day - 1) // 7 + 1
        result = await db_session.execute(
            select(WeeklyReport).where(
                WeeklyReport.user_id == user.id, WeeklyReport.week_number == week_number
            )
        )
        report = result.scalar_one()
        assert report.content["week_number"] == week_number

    @pytest.mark.asyncio
    async def test_idempotent_report_generation(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        user = await _create_onboarded_user(client, db_session, program_day=8)

        plan = Plan(user_id=user.id, season=1, program_name="Test Plan")
        db_session.add(plan)
        await db_session.flush()

        for i in range(7):
            task = DailyTask(
                user_id=user.id,
                plan_id=plan.id,
                title=f"Task {i}",
                category="routine",
                pillar="skin",
                day_number=i + 1,
                is_completed=True,
                completed_at=datetime.now(UTC),
            )
            db_session.add(task)
        await db_session.flush()

        await generate_weekly_reports(db_session)
        count2 = await generate_weekly_reports(db_session)
        assert count2 == 0
