"""Gamification service — achievements, challenges, streak, and XP logic."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Achievement, ChallengeProgress, Cycle, DailyTask, Progress
from src.gamification.badges import BADGE_CATALOG, STREAK_BADGE_IDS, get_badges_for_condition
from src.gamification.challenges import CHALLENGE_CATALOG, get_available_challenges
from src.gamification.schemas import (
    AchievementsResponse,
    BadgeResponse,
    ChallengeResponse,
    ChallengesListResponse,
    StartChallengeRequest,
    StreakResponse,
    XPResponse,
)
from src.gamification.xp import calculate_level, get_level_name, xp_for_next_level

STREAK_MILESTONES = [3, 7, 14, 30, 60, 90]


async def get_achievements(user_id: uuid.UUID, db: AsyncSession) -> AchievementsResponse:
    """Get all badges with unlock status for the user."""
    stmt = select(Achievement).where(Achievement.user_id == user_id)
    result = await db.execute(stmt)
    unlocked = {a.badge_id: a.unlocked_at for a in result.scalars().all()}

    badges = []
    for badge in BADGE_CATALOG.values():
        badges.append(
            BadgeResponse(
                badge_id=badge.badge_id,
                name=badge.name,
                description=badge.description,
                icon=badge.icon,
                category=badge.category,
                unlocked=badge.badge_id in unlocked,
                unlocked_at=unlocked.get(badge.badge_id),
            )
        )

    return AchievementsResponse(
        badges=badges,
        total_unlocked=len(unlocked),
        total_available=len(BADGE_CATALOG),
    )


async def unlock_badges_for_event(
    user_id: uuid.UUID,
    condition_type: str,
    value: int,
    db: AsyncSession,
) -> list[str]:
    """Check and unlock any badges that should be awarded for this event."""
    eligible = get_badges_for_condition(condition_type, value)
    if not eligible:
        return []

    stmt = select(Achievement.badge_id).where(Achievement.user_id == user_id)
    result = await db.execute(stmt)
    already_unlocked = set(result.scalars().all())

    newly_unlocked = []
    for badge in eligible:
        if badge.badge_id not in already_unlocked:
            achievement = Achievement(
                user_id=user_id,
                badge_id=badge.badge_id,
                unlocked_at=datetime.now(UTC),
            )
            db.add(achievement)
            newly_unlocked.append(badge.badge_id)

    return newly_unlocked


async def get_challenges(user_id: uuid.UUID, db: AsyncSession) -> ChallengesListResponse:
    """Get active, available, and completed challenge counts."""
    stmt = select(ChallengeProgress).where(ChallengeProgress.user_id == user_id)
    result = await db.execute(stmt)
    user_challenges = result.scalars().all()

    active_ids = set()
    completed_ids = set()
    active_list = []

    for cp in user_challenges:
        if cp.status == "active":
            active_ids.add(cp.challenge_id)
            template = _find_template(cp.challenge_id)
            if template:
                active_list.append(
                    ChallengeResponse(
                        id=cp.id,
                        challenge_id=cp.challenge_id,
                        name=template.name,
                        description=template.description,
                        icon=template.icon,
                        target=cp.target,
                        progress=cp.progress,
                        duration_days=template.duration_days,
                        xp_reward=template.xp_reward,
                        status="active",
                        started_at=cp.started_at,
                        pillar=template.pillar,
                    )
                )
        elif cp.status == "completed":
            completed_ids.add(cp.challenge_id)

    available_templates = get_available_challenges(active_ids, completed_ids)
    available_list = [
        ChallengeResponse(
            challenge_id=t.challenge_id,
            name=t.name,
            description=t.description,
            icon=t.icon,
            target=t.target,
            progress=0,
            duration_days=t.duration_days,
            xp_reward=t.xp_reward,
            status="available",
            pillar=t.pillar,
        )
        for t in available_templates
    ]

    return ChallengesListResponse(
        active=active_list,
        available=available_list,
        completed_count=len(completed_ids),
    )


async def start_challenge(
    user_id: uuid.UUID,
    request: StartChallengeRequest,
    db: AsyncSession,
) -> ChallengeResponse:
    """Start a new challenge for the user."""
    template = _find_template(request.challenge_id)
    if template is None:
        raise ChallengeNotFoundError(f"Challenge '{request.challenge_id}' not found")

    existing = await db.execute(
        select(ChallengeProgress).where(
            ChallengeProgress.user_id == user_id,
            ChallengeProgress.challenge_id == request.challenge_id,
            ChallengeProgress.status == "active",
        )
    )
    if existing.scalar_one_or_none():
        raise ChallengeAlreadyActiveError("Challenge is already active")

    cp = ChallengeProgress(
        user_id=user_id,
        challenge_id=request.challenge_id,
        status="active",
        progress=0,
        target=template.target,
        started_at=datetime.now(UTC),
    )
    db.add(cp)
    await db.flush()

    return ChallengeResponse(
        id=cp.id,
        challenge_id=cp.challenge_id,
        name=template.name,
        description=template.description,
        icon=template.icon,
        target=cp.target,
        progress=0,
        duration_days=template.duration_days,
        xp_reward=template.xp_reward,
        status="active",
        started_at=cp.started_at,
        pillar=template.pillar,
    )


async def update_challenge_progress(
    user_id: uuid.UUID,
    challenge_id: str,
    increment: int,
    db: AsyncSession,
) -> bool:
    """Increment challenge progress. Returns True if challenge was just completed."""
    stmt = select(ChallengeProgress).where(
        ChallengeProgress.user_id == user_id,
        ChallengeProgress.challenge_id == challenge_id,
        ChallengeProgress.status == "active",
    )
    result = await db.execute(stmt)
    cp = result.scalar_one_or_none()

    if cp is None:
        return False

    cp.progress = min(cp.progress + increment, cp.target)

    if cp.progress >= cp.target:
        cp.status = "completed"
        cp.completed_at = datetime.now(UTC)
        return True

    return False


async def get_streak_info(user_id: uuid.UUID, db: AsyncSession) -> StreakResponse:
    """Get streak data and milestone info for the user."""
    stmt = select(Progress).where(Progress.user_id == user_id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    current = progress.current_streak if progress else 0
    longest = progress.longest_streak if progress else 0

    stmt = select(Achievement.badge_id).where(
        Achievement.user_id == user_id,
        Achievement.badge_id.in_(STREAK_BADGE_IDS),
    )
    result = await db.execute(stmt)
    streak_badges = list(result.scalars().all())

    next_milestone = None
    for m in STREAK_MILESTONES:
        if current < m:
            next_milestone = m
            break

    return StreakResponse(
        current_streak=current,
        longest_streak=longest,
        milestones=STREAK_MILESTONES,
        next_milestone=next_milestone,
        streak_badges_unlocked=streak_badges,
    )


async def get_xp_info(user_id: uuid.UUID, db: AsyncSession) -> XPResponse:
    """Get XP and level breakdown for the user."""
    stmt = select(Progress).where(Progress.user_id == user_id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    total_xp = progress.total_xp if progress else 0
    info = xp_for_next_level(total_xp)

    return XPResponse(
        total_xp=info["xp_current"],
        current_level=info["current_level"],
        level_name=info["level_name"],
        xp_progress=info["xp_progress"],
        xp_needed=info["xp_needed"],
        progress_pct=info["progress_pct"],
        xp_for_next_level=info["xp_for_next_level"],
    )


async def get_tasks_completed_count(user_id: uuid.UUID, db: AsyncSession) -> int:
    """Count total completed tasks for a user."""
    stmt = select(func.count()).where(
        DailyTask.user_id == user_id,
        DailyTask.is_completed.is_(True),
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def get_cycles_completed_count(user_id: uuid.UUID, db: AsyncSession) -> int:
    """Count total completed cycles for a user."""
    stmt = select(func.count()).where(Cycle.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar() or 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_template(challenge_id: str):
    """Look up a challenge template by ID."""
    for t in CHALLENGE_CATALOG:
        if t.challenge_id == challenge_id:
            return t
    return None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ChallengeNotFoundError(Exception):
    pass


class ChallengeAlreadyActiveError(Exception):
    pass


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Gamification service — badges, challenges, streaks, XP/level tracking.

Flow:
1. get_achievements() — returns all badges with unlock status
2. unlock_badges_for_event() — checks conditions and unlocks eligible badges (idempotent)
3. get_challenges() / start_challenge() / update_challenge_progress() — challenge lifecycle
4. get_streak_info() / get_xp_info() — streak milestones and XP progress

Main Entry Point: get_achievements, unlock_badges_for_event, get_challenges, start_challenge

Dependencies:
- src.database.models: Achievement, ChallengeProgress, Progress
- src.gamification.badges: badge catalog and condition matching
- src.gamification.challenges: challenge templates
- src.gamification.xp: level calculation
"""
