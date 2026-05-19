from decimal import Decimal

from pydantic import BaseModel


class PillarScore(BaseModel):
    pillar: str
    label: str
    score: int
    delta_vs_baseline: int
    weight: float


class ProgressResponse(BaseModel):
    optimisation_score: Decimal
    delta_vs_baseline: Decimal
    current_streak: int
    longest_streak: int
    total_xp: int
    level: int
    pillar_scores: list[PillarScore]


class PillarHistoryPoint(BaseModel):
    day_number: int
    score: int


class PillarDetailResponse(BaseModel):
    pillar: str
    label: str
    score: int
    delta_vs_baseline: int
    weight: float
    rank: int
    tasks_completed: int
    history: list[PillarHistoryPoint]


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Pydantic response schemas for the progress endpoints.

Flow:
1. ProgressResponse — full user progress snapshot (all pillars + XP + streak)
2. PillarDetailResponse — deep-dive on a single pillar with task history

Main Entry Point: ProgressResponse, PillarDetailResponse

Dependencies:
- pydantic: validation and serialization
"""
