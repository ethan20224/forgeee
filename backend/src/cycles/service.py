"""Cycle check-in service — orchestrates photo upload, analysis, and history."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cycles.photo_analyser import analyse_photos
from src.cycles.schemas import (
    CycleAnalysisResponse,
    CycleCompareResponse,
    CycleHistoryItem,
    CycleHistoryResponse,
    EligibilityResponse,
    PillarScores,
    UploadUrlResponse,
)
from src.database.models import Cycle, Progress, User
from src.storage.r2_client import generate_download_url, generate_upload_url

CYCLE_COOLDOWN_DAYS = 7
PILLAR_SCORE_FIELDS = [
    "facial_composition_score",
    "skin_score",
    "grooming_score",
    "hair_score",
    "posture_score",
    "style_score",
    "sleep_score",
    "nutrition_score",
    "voice_score",
]


async def get_upload_url(user_id: uuid.UUID, angle: str = "front") -> UploadUrlResponse:
    """Generate a presigned URL for photo upload."""
    result = generate_upload_url(user_id, angle)
    return UploadUrlResponse(**result)


async def check_eligibility(user_id: uuid.UUID, db: AsyncSession) -> EligibilityResponse:
    """Check whether the user can submit a new cycle check-in."""
    latest = await _get_latest_cycle(user_id, db)

    if latest is None:
        return EligibilityResponse(
            eligible=True,
            next_eligible_at=None,
            reason=None,
            current_cycle_number=1,
        )

    next_eligible = latest.checked_in_at + timedelta(days=CYCLE_COOLDOWN_DAYS)
    now = datetime.now(UTC)

    if now >= next_eligible:
        return EligibilityResponse(
            eligible=True,
            next_eligible_at=None,
            reason=None,
            current_cycle_number=latest.cycle_number + 1,
        )

    return EligibilityResponse(
        eligible=False,
        next_eligible_at=next_eligible,
        reason=f"Next check-in available in {(next_eligible - now).days + 1} days",
        current_cycle_number=latest.cycle_number,
    )


async def submit_analysis(
    user_id: uuid.UUID,
    object_key: str,
    scan_mode: str,
    db: AsyncSession,
) -> CycleAnalysisResponse:
    """
    Analyse a photo and create a cycle record.

    Generates a download URL, sends to VL2, stores scores in DB,
    and updates Progress pillar scores.
    """
    eligibility = await check_eligibility(user_id, db)
    if not eligibility.eligible:
        raise CycleNotEligibleError(eligibility.reason or "Not eligible yet")

    photo_url = generate_download_url(object_key)

    analysis = await analyse_photos(photo_url, scan_mode)

    cycle_number = eligibility.current_cycle_number
    cycle = Cycle(
        user_id=user_id,
        cycle_number=cycle_number,
        photo_path=object_key,
        cycle_type=scan_mode,
        face_shape=analysis.get("face_shape"),
        facial_composition_score=analysis.get("facial_composition_score"),
        skin_score=analysis.get("skin_score"),
        grooming_score=analysis.get("grooming_score"),
        hair_score=analysis.get("hair_score"),
        posture_score=analysis.get("posture_score"),
        style_score=analysis.get("style_score"),
        sleep_score=analysis.get("sleep_score"),
        nutrition_score=analysis.get("nutrition_score"),
        voice_score=analysis.get("voice_score"),
        ai_insight=analysis.get("ai_insight"),
        next_focus=analysis.get("next_focus"),
    )
    db.add(cycle)

    await _update_progress_scores(user_id, analysis, db)

    if analysis.get("face_shape"):
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
        user.face_shape = analysis["face_shape"]

    await db.commit()
    await db.refresh(cycle)

    return CycleAnalysisResponse(
        cycle_id=cycle.id,
        cycle_number=cycle.cycle_number,
        scan_mode=scan_mode,
        scores=PillarScores(
            facial_composition_score=cycle.facial_composition_score,
            skin_score=cycle.skin_score,
            grooming_score=cycle.grooming_score,
            hair_score=cycle.hair_score,
            posture_score=cycle.posture_score,
            style_score=cycle.style_score,
            sleep_score=cycle.sleep_score,
            nutrition_score=cycle.nutrition_score,
            voice_score=cycle.voice_score,
        ),
        face_shape=cycle.face_shape,
        ai_insight=cycle.ai_insight,
        next_focus=cycle.next_focus,
        checked_in_at=cycle.checked_in_at,
    )


async def get_history(
    user_id: uuid.UUID,
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> CycleHistoryResponse:
    """Fetch cycle history for a user, most recent first."""
    count_stmt = select(func.count()).where(Cycle.user_id == user_id)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Cycle)
        .where(Cycle.user_id == user_id)
        .order_by(Cycle.cycle_number.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    cycles = result.scalars().all()

    items = [
        CycleHistoryItem(
            cycle_id=c.id,
            cycle_number=c.cycle_number,
            cycle_type=c.cycle_type,
            face_shape=c.face_shape,
            optimisation_score=_avg_scores(c),
            checked_in_at=c.checked_in_at,
        )
        for c in cycles
    ]

    return CycleHistoryResponse(cycles=items, total=total)


async def get_cycle_detail(
    user_id: uuid.UUID,
    cycle_id: uuid.UUID,
    db: AsyncSession,
) -> CycleAnalysisResponse:
    """Fetch a single cycle analysis by ID."""
    stmt = select(Cycle).where(Cycle.id == cycle_id, Cycle.user_id == user_id)
    result = await db.execute(stmt)
    cycle = result.scalar_one_or_none()

    if cycle is None:
        raise CycleNotFoundError(f"Cycle {cycle_id} not found")

    return CycleAnalysisResponse(
        cycle_id=cycle.id,
        cycle_number=cycle.cycle_number,
        scan_mode=cycle.cycle_type,
        scores=PillarScores(
            facial_composition_score=cycle.facial_composition_score,
            skin_score=cycle.skin_score,
            grooming_score=cycle.grooming_score,
            hair_score=cycle.hair_score,
            posture_score=cycle.posture_score,
            style_score=cycle.style_score,
            sleep_score=cycle.sleep_score,
            nutrition_score=cycle.nutrition_score,
            voice_score=cycle.voice_score,
        ),
        face_shape=cycle.face_shape,
        ai_insight=cycle.ai_insight,
        next_focus=cycle.next_focus,
        checked_in_at=cycle.checked_in_at,
    )


async def compare_cycles(
    user_id: uuid.UUID,
    current_id: uuid.UUID,
    previous_id: uuid.UUID,
    db: AsyncSession,
) -> CycleCompareResponse:
    """Compare two cycles and return score deltas."""
    current = await _get_cycle(user_id, current_id, db)
    previous = await _get_cycle(user_id, previous_id, db)

    current_scores = _extract_scores(current)
    previous_scores = _extract_scores(previous)
    deltas = {}

    for field in PILLAR_SCORE_FIELDS:
        c_val = getattr(current, field)
        p_val = getattr(previous, field)
        if c_val is not None and p_val is not None:
            deltas[field.replace("_score", "")] = c_val - p_val
        else:
            deltas[field.replace("_score", "")] = None

    days_between = (current.checked_in_at - previous.checked_in_at).days

    return CycleCompareResponse(
        current=current_scores,
        previous=previous_scores,
        deltas=deltas,
        days_between=abs(days_between),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_latest_cycle(user_id: uuid.UUID, db: AsyncSession) -> Cycle | None:
    stmt = (
        select(Cycle)
        .where(Cycle.user_id == user_id)
        .order_by(Cycle.cycle_number.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_cycle(user_id: uuid.UUID, cycle_id: uuid.UUID, db: AsyncSession) -> Cycle:
    stmt = select(Cycle).where(Cycle.id == cycle_id, Cycle.user_id == user_id)
    result = await db.execute(stmt)
    cycle = result.scalar_one_or_none()
    if cycle is None:
        raise CycleNotFoundError(f"Cycle {cycle_id} not found")
    return cycle


async def _update_progress_scores(
    user_id: uuid.UUID,
    analysis: dict,
    db: AsyncSession,
) -> None:
    """Update the user's Progress pillar scores from cycle analysis."""
    stmt = select(Progress).where(Progress.user_id == user_id)
    result = await db.execute(stmt)
    progress = result.scalar_one_or_none()

    if progress is None:
        return

    for field in PILLAR_SCORE_FIELDS:
        new_val = analysis.get(field)
        if new_val is not None:
            setattr(progress, field, new_val)


def _extract_scores(cycle: Cycle) -> PillarScores:
    return PillarScores(
        facial_composition_score=cycle.facial_composition_score,
        skin_score=cycle.skin_score,
        grooming_score=cycle.grooming_score,
        hair_score=cycle.hair_score,
        posture_score=cycle.posture_score,
        style_score=cycle.style_score,
        sleep_score=cycle.sleep_score,
        nutrition_score=cycle.nutrition_score,
        voice_score=cycle.voice_score,
    )


def _avg_scores(cycle: Cycle) -> float | None:
    """Calculate average of non-null pillar scores for a cycle."""
    values = [
        getattr(cycle, f) for f in PILLAR_SCORE_FIELDS if getattr(cycle, f) is not None
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class CycleNotEligibleError(Exception):
    """Raised when user attempts a check-in before cooldown expires."""

    pass


class CycleNotFoundError(Exception):
    """Raised when a cycle is not found for the user."""

    pass


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Cycle check-in business logic — upload URLs, analysis, history, comparisons.

Flow:
1. get_upload_url() → presigned PUT URL for direct browser upload
2. submit_analysis() → checks eligibility, calls VL2, stores Cycle, updates Progress
3. get_history() → paginated list of past cycles
4. compare_cycles() → delta scores between two cycles

Main Entry Point: submit_analysis, get_upload_url, get_history, compare_cycles

Dependencies:
- src.storage.r2_client: presigned URLs
- src.cycles.photo_analyser: VL2 analysis
- src.database.models: Cycle, Progress, User ORM models
"""
