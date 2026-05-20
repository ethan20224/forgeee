"""Pydantic schemas for cycle check-in endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    """Request body for generating a presigned upload URL."""

    angle: str = Field(default="front", pattern="^(front|side|full)$")
    scan_mode: str = Field(default="face", pattern="^(face|full)$")


class UploadUrlResponse(BaseModel):
    """Presigned URL response for direct upload."""

    upload_url: str
    object_key: str
    expires_in: int


class AnalyseRequest(BaseModel):
    """Request to trigger photo analysis on an uploaded image."""

    object_key: str
    scan_mode: str = Field(default="face", pattern="^(face|full)$")


class PillarScores(BaseModel):
    """Score breakdown for a cycle analysis."""

    facial_composition_score: int | None = None
    skin_score: int | None = None
    grooming_score: int | None = None
    hair_score: int | None = None
    posture_score: int | None = None
    style_score: int | None = None
    sleep_score: int | None = None
    nutrition_score: int | None = None
    voice_score: int | None = None


class CycleAnalysisResponse(BaseModel):
    """Full cycle analysis result."""

    cycle_id: uuid.UUID
    cycle_number: int
    scan_mode: str
    scores: PillarScores
    face_shape: str | None = None
    ai_insight: str | None = None
    next_focus: str | None = None
    checked_in_at: datetime


class CycleHistoryItem(BaseModel):
    """Summary item for cycle history list."""

    cycle_id: uuid.UUID
    cycle_number: int
    cycle_type: str
    face_shape: str | None = None
    optimisation_score: float | None = None
    checked_in_at: datetime


class CycleHistoryResponse(BaseModel):
    """Paginated list of cycle analyses."""

    cycles: list[CycleHistoryItem]
    total: int


class CycleCompareResponse(BaseModel):
    """Comparison between two cycles showing score deltas."""

    current: PillarScores
    previous: PillarScores
    deltas: dict[str, int | None]
    days_between: int


class EligibilityResponse(BaseModel):
    """Whether the user can submit a new cycle check-in."""

    eligible: bool
    next_eligible_at: datetime | None = None
    reason: str | None = None
    current_cycle_number: int
