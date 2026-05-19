import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DailyTaskOut(BaseModel):
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
    library_task_id: str | None

    model_config = {"from_attributes": True}


class PlanDetail(BaseModel):
    id: uuid.UUID
    season: int
    program_name: str | None
    focus_summary: str | None
    honest_expectation: str | None
    created_at: datetime
    daily_tasks: list[DailyTaskOut] = []

    model_config = {"from_attributes": True}


class GeneratePlanResponse(BaseModel):
    plan: PlanDetail
    from_cache: bool


class PlanSummary(BaseModel):
    id: uuid.UUID
    season: int
    program_name: str | None
    focus_summary: str | None
    created_at: datetime
    task_count: int

    model_config = {"from_attributes": True}


class LLMPlanWeek(BaseModel):
    """Schema for one week in the LLM JSON response."""

    week: int
    days: list["LLMPlanDay"]


class LLMPlanDay(BaseModel):
    """Schema for one day in the LLM JSON response."""

    day: int
    tasks: list["LLMPlanTask"]


class LLMPlanTask(BaseModel):
    """Schema for one task in the LLM JSON response."""

    library_task_id: str
    pillar: str
    tier: str = "beginner"


class LLMPlanOutput(BaseModel):
    """Top-level schema returned by the LLM."""

    program_name: str = Field(max_length=100)
    focus_summary: str = Field(max_length=300)
    honest_expectation: str = Field(max_length=300)
    weeks: list[LLMPlanWeek]
