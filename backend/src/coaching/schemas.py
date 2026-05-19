from datetime import datetime

from pydantic import BaseModel


class InsightResponse(BaseModel):
    stage: str
    context_type: str
    pillar: str | None
    message: str
    program_day: int


class PillarMovement(BaseModel):
    pillar: str
    label: str
    score: int
    delta: int


class WeeklyReportResponse(BaseModel):
    week_number: int
    season: int
    completion_rate: float
    completed_tasks: int
    total_tasks: int
    pillar_movements: list[PillarMovement]
    coaching_note: str
    focus_next_week: str
    generated_at: datetime | None = None


class WeeklyReportSummary(BaseModel):
    week_number: int
    season: int
    completion_rate: float
    generated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SeasonReportResponse(BaseModel):
    season: int
    opening: str
    biggest_mover: str
    needs_work: str
    next_focus: str
    score_start: int
    score_end: int
    score_delta: int
    total_tasks_completed: int
    completion_rate: float
    streak_best: int


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Pydantic response schemas for coaching endpoints.

Flow:
1. InsightResponse — single daily insight
2. WeeklyReportResponse — full weekly report with coaching paragraphs
3. SeasonReportResponse — end-of-season narrative report

Main Entry Point: InsightResponse, WeeklyReportResponse, SeasonReportResponse

Dependencies:
- pydantic: validation and serialization
"""
