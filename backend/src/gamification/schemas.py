"""Pydantic schemas for gamification endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class BadgeResponse(BaseModel):
    badge_id: str
    name: str
    description: str
    icon: str
    category: str
    unlocked: bool
    unlocked_at: datetime | None = None


class AchievementsResponse(BaseModel):
    badges: list[BadgeResponse]
    total_unlocked: int
    total_available: int


class ChallengeResponse(BaseModel):
    id: uuid.UUID | None = None
    challenge_id: str
    name: str
    description: str
    icon: str
    target: int
    progress: int
    duration_days: int
    xp_reward: int
    status: str
    started_at: datetime | None = None
    pillar: str | None = None


class ChallengesListResponse(BaseModel):
    active: list[ChallengeResponse]
    available: list[ChallengeResponse]
    completed_count: int


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    milestones: list[int]
    next_milestone: int | None
    streak_badges_unlocked: list[str]


class XPResponse(BaseModel):
    total_xp: int
    current_level: int
    level_name: str
    xp_progress: int
    xp_needed: int
    progress_pct: float
    xp_for_next_level: int | None


class StartChallengeRequest(BaseModel):
    challenge_id: str
