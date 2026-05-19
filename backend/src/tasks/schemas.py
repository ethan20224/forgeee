import uuid
from datetime import datetime

from pydantic import BaseModel


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    category: str
    pillar: str
    tier: str
    why_it_works: str | None
    duration_mins: int | None
    day_number: int
    week_number: int | None
    xp_value: int
    is_completed: bool
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class CompleteTaskResponse(BaseModel):
    task_id: uuid.UUID
    xp_earned: int
    streak_bonus: int
    total_xp: int
    new_streak: int
    level: int
    pillar_affected: str
    new_pillar_score: int
    streak_milestone: int | None = None


class HeatmapDay(BaseModel):
    day_number: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    primary_pillar: str | None = None


class HeatmapResponse(BaseModel):
    days: list[HeatmapDay]
    total_days: int
    overall_completion_rate: float


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Pydantic request/response schemas for the task engine endpoints.

Flow:
1. TaskResponse — single task representation for GET /today
2. CompleteTaskResponse — result of completing a task (XP, streak, drift)
3. HeatmapDay/HeatmapResponse — 90-day completion grid data

Main Entry Point: TaskResponse, CompleteTaskResponse, HeatmapResponse

Dependencies:
- pydantic: validation and serialization
"""
