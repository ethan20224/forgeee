import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QuizSubmitRequest(BaseModel):
    goals: list[str] = Field(min_length=1, max_length=9)
    routine_level: str = Field(pattern=r"^(none|basic|moderate|advanced)$")
    daily_time: str = Field(pattern=r"^(10min|20min|30min|45min|60min)$")
    timeline: str = Field(pattern=r"^(30days|60days|90days)$")
    main_concern: str = Field(pattern=r"^(skin|hair|grooming|style|posture|overall)$")
    age_range: str = Field(pattern=r"^(16-19|20-24|25-29|30-34|35-39|40\+)$")
    has_photo: bool = False


class QuizAnswerResponse(BaseModel):
    id: uuid.UUID
    goals: list[str] | None
    routine_level: str | None
    daily_time: str | None
    timeline: str | None
    main_concern: str | None
    age_range: str | None
    has_photo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PillarEstimate(BaseModel):
    pillar: str
    score: int
    label: str


class ScoreEstimateResponse(BaseModel):
    pillar_scores: list[PillarEstimate]
    optimisation_score: float
    tier: str
    summary: str
