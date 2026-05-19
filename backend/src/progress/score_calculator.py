"""Deterministic scoring engine for FORGE pillar scores and optimisation score."""

from decimal import Decimal

from src.common.constants import PILLARS

FACE_SHAPE_WEIGHTS: dict[str, dict[str, float]] = {
    "oval": {
        "facial_composition": 0.15, "skin": 0.12, "grooming": 0.12,
        "hair": 0.12, "posture": 0.10, "style": 0.12,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.03,
    },
    "square": {
        "facial_composition": 0.12, "skin": 0.15, "grooming": 0.10,
        "hair": 0.10, "posture": 0.10, "style": 0.15,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.04,
    },
    "round": {
        "facial_composition": 0.12, "skin": 0.12, "grooming": 0.15,
        "hair": 0.15, "posture": 0.10, "style": 0.12,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.00,
    },
    "long": {
        "facial_composition": 0.14, "skin": 0.12, "grooming": 0.10,
        "hair": 0.10, "posture": 0.15, "style": 0.12,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.03,
    },
    "oblong": {
        "facial_composition": 0.14, "skin": 0.12, "grooming": 0.10,
        "hair": 0.10, "posture": 0.15, "style": 0.12,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.03,
    },
    "heart": {
        "facial_composition": 0.12, "skin": 0.15, "grooming": 0.14,
        "hair": 0.12, "posture": 0.10, "style": 0.12,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.02,
    },
    "diamond": {
        "facial_composition": 0.12, "skin": 0.12, "grooming": 0.12,
        "hair": 0.12, "posture": 0.12, "style": 0.12,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.02,
    },
    "triangle": {
        "facial_composition": 0.12, "skin": 0.12, "grooming": 0.12,
        "hair": 0.14, "posture": 0.12, "style": 0.12,
        "sleep": 0.12, "nutrition": 0.12, "voice": 0.02,
    },
}

CONCERN_BOOSTS: dict[str, dict[str, float]] = {
    "skin": {"skin": 0.05},
    "grooming": {"grooming": 0.05},
    "hair": {"hair": 0.05},
    "posture": {"posture": 0.05, "style": 0.05},
    "style": {"style": 0.05, "posture": 0.05},
    "overall": {},
}


def derive_initial_weights(
    face_shape: str | None = None,
    main_concern: str | None = None,
    season: int = 1,
) -> dict[str, float]:
    """
    Derive personalised pillar weights from face shape and quiz concern.

    Steps:
    1. Start with face shape weights (or equal 1/9 distribution)
    2. Apply quiz concern boost (+0.05 to relevant pillars)
    3. Apply seasonal reweight (voice excluded in Season 1)
    4. Normalise to sum = 1.0
    """
    if face_shape and face_shape.lower() in FACE_SHAPE_WEIGHTS:
        weights = dict(FACE_SHAPE_WEIGHTS[face_shape.lower()])
    else:
        base = 1.0 / len(PILLARS)
        weights = {p: base for p in PILLARS}

    if main_concern and main_concern in CONCERN_BOOSTS:
        for pillar, boost in CONCERN_BOOSTS[main_concern].items():
            weights[pillar] = weights.get(pillar, 0) + boost

    weights = apply_seasonal_reweight(weights, season)

    return _normalise_weights(weights)


def apply_seasonal_reweight(
    weights: dict[str, float],
    season: int,
) -> dict[str, float]:
    """
    Season 1: voice has weight 0 (excluded from score).
    Season 2+: voice gets standard weight, others reduced proportionally.
    """
    if season <= 1:
        weights["voice"] = 0.0
    else:
        if weights.get("voice", 0) == 0:
            weights["voice"] = 0.11

    return weights


def calculate_optimisation_score(
    pillar_scores: dict[str, int | None],
    weights: dict[str, float],
) -> Decimal:
    """
    Compute weighted optimisation score from pillar scores and weights.

    Null pillars are excluded (their weight redistributed to non-null pillars).
    If all pillars are null, returns 50 (baseline).
    """
    weighted_sum = 0.0
    weight_sum = 0.0

    for pillar in PILLARS:
        score = pillar_scores.get(pillar)
        weight = weights.get(pillar, 0)
        if score is not None and weight > 0:
            weighted_sum += score * weight
            weight_sum += weight

    if weight_sum == 0:
        return Decimal("50.00")

    result = weighted_sum / weight_sum
    return Decimal(str(round(clamp(result, 0, 100), 2)))


def diff_pillars(
    current: dict[str, int | None],
    previous: dict[str, int | None],
) -> dict[str, int | None]:
    """
    Compute per-pillar deltas between two score snapshots.
    Returns None for any pillar where either score is None.
    """
    deltas: dict[str, int | None] = {}
    for pillar in PILLARS:
        cur = current.get(pillar)
        prev = previous.get(pillar)
        if cur is not None and prev is not None:
            deltas[pillar] = clamp(cur - prev, -100, 100)
        else:
            deltas[pillar] = None
    return deltas


def clamp(value: float | int, min_val: float | int, max_val: float | int) -> float:
    """Clamp a value to [min_val, max_val]."""
    return max(min_val, min(value, max_val))


def _normalise_weights(weights: dict[str, float]) -> dict[str, float]:
    """Normalise weights to sum to exactly 1.0."""
    total = sum(weights.values())
    if total == 0:
        base = 1.0 / len(PILLARS)
        return {p: base for p in PILLARS}
    return {p: w / total for p, w in weights.items()}


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Deterministic scoring engine for FORGE. Handles pillar weight
derivation (face shape + concern + season), weighted optimisation score
calculation, pillar diff computation, and score clamping.

Flow:
1. derive_initial_weights() — builds personalised weights from face shape + concern
2. apply_seasonal_reweight() — excludes voice in S1, includes in S2+
3. calculate_optimisation_score() — weighted average with null-pillar exclusion
4. diff_pillars() — delta between two score snapshots
5. clamp() — bounds enforcement

Main Entry Point: derive_initial_weights, calculate_optimisation_score

Dependencies:
- src.common.constants: PILLARS list
"""
