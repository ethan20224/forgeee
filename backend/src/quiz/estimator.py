"""Deterministic score estimator — no LLM needed.

Estimates starting pillar scores from quiz answers using heuristic rules.
Scores range 0-100, default baseline 50.
"""

from src.common.constants import PILLAR_LABELS, PILLARS

# Baseline for all pillars
_BASE = 50

# How routine_level shifts the baseline
_ROUTINE_SHIFT: dict[str, int] = {
    "none": -15,
    "basic": -5,
    "moderate": 5,
    "advanced": 12,
}

# Bonus for having a photo (shows commitment)
_PHOTO_BONUS = 3

# Goals boost the selected pillars
_GOAL_BOOST = 5

# The user's main concern gets a penalty (they self-identified it as weak)
_CONCERN_PENALTY = -8

# Age-related adjustments: younger = slightly higher skin/hair baseline
_AGE_SKIN_HAIR: dict[str, int] = {
    "16-19": 6,
    "20-24": 4,
    "25-29": 2,
    "30-34": 0,
    "35-39": -2,
    "40+": -4,
}

# Daily time commitment boosts all scores slightly
_TIME_BOOST: dict[str, int] = {
    "10min": -3,
    "20min": 0,
    "30min": 2,
    "45min": 4,
    "60min": 6,
}

# Map concern names to pillar keys
_CONCERN_TO_PILLAR: dict[str, list[str]] = {
    "skin": ["skin"],
    "hair": ["hair"],
    "grooming": ["grooming"],
    "style": ["style"],
    "posture": ["posture"],
    "overall": [],
}


def _clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, value))


def estimate_scores(
    goals: list[str],
    routine_level: str,
    daily_time: str,
    main_concern: str,
    age_range: str,
    has_photo: bool,
) -> dict[str, int]:
    """Return a dict of pillar → estimated score (0-100)."""
    scores: dict[str, int] = {}
    routine_shift = _ROUTINE_SHIFT.get(routine_level, 0)
    time_boost = _TIME_BOOST.get(daily_time, 0)
    age_adj = _AGE_SKIN_HAIR.get(age_range, 0)
    concern_pillars = _CONCERN_TO_PILLAR.get(main_concern, [])

    for pillar in PILLARS:
        score = _BASE + routine_shift + time_boost

        if has_photo:
            score += _PHOTO_BONUS

        if pillar in goals:
            score += _GOAL_BOOST

        if pillar in concern_pillars:
            score += _CONCERN_PENALTY

        if main_concern == "overall":
            score -= 3

        if pillar in ("skin", "hair"):
            score += age_adj

        scores[pillar] = _clamp(score)

    return scores


def compute_optimisation_score(pillar_scores: dict[str, int]) -> float:
    """Weighted average of pillar scores. Returns 0-100."""
    if not pillar_scores:
        return 50.0
    total = sum(pillar_scores.values())
    return round(total / len(pillar_scores), 2)


def determine_tier(optimisation_score: float) -> str:
    if optimisation_score >= 70:
        return "advanced"
    if optimisation_score >= 45:
        return "intermediate"
    return "beginner"


def generate_summary(
    tier: str,
    main_concern: str,
    optimisation_score: float,
) -> str:
    """One-liner summary for the user."""
    concern_label = PILLAR_LABELS.get(main_concern, main_concern.title())
    if tier == "advanced":
        return (
            f"Strong foundation at {optimisation_score:.0f}/100. "
            f"Focus on {concern_label} refinement for your next season."
        )
    if tier == "intermediate":
        return (
            f"Solid base at {optimisation_score:.0f}/100. "
            f"Your {concern_label} area has the most room for growth."
        )
    return (
        f"Starting at {optimisation_score:.0f}/100. "
        f"We'll build from {concern_label} fundamentals first."
    )


def full_estimate(
    goals: list[str],
    routine_level: str,
    daily_time: str,
    main_concern: str,
    age_range: str,
    has_photo: bool,
) -> dict:
    """Return full estimate payload ready for the API response."""
    pillar_scores = estimate_scores(
        goals, routine_level, daily_time, main_concern, age_range, has_photo
    )
    opt_score = compute_optimisation_score(pillar_scores)
    tier = determine_tier(opt_score)
    summary = generate_summary(tier, main_concern, opt_score)

    return {
        "pillar_scores": [
            {"pillar": p, "score": s, "label": PILLAR_LABELS[p]} for p, s in pillar_scores.items()
        ],
        "optimisation_score": opt_score,
        "tier": tier,
        "summary": summary,
    }
