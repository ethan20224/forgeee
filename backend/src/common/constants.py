"""Shared constants used across the FORGE backend."""

PILLARS: list[str] = [
    "skin",
    "hair",
    "grooming",
    "facial_composition",
    "posture",
    "style",
    "sleep",
    "nutrition",
    "voice",
]

PILLAR_LABELS: dict[str, str] = {
    "skin": "Skin",
    "hair": "Hair",
    "grooming": "Grooming",
    "facial_composition": "Facial Composition",
    "posture": "Posture",
    "style": "Style",
    "sleep": "Sleep",
    "nutrition": "Nutrition",
    "voice": "Voice",
}

PILLAR_DB_FIELDS: dict[str, str] = {
    "skin": "skin_score",
    "hair": "hair_score",
    "grooming": "grooming_score",
    "facial_composition": "facial_composition_score",
    "posture": "posture_score",
    "style": "style_score",
    "sleep": "sleep_score",
    "nutrition": "nutrition_score",
    "voice": "voice_score",
}

TIERS: list[str] = ["beginner", "intermediate", "advanced"]

ROUTINE_LEVELS: list[str] = ["none", "basic", "moderate", "advanced"]

DAILY_TIME_OPTIONS: list[str] = ["10min", "20min", "30min", "45min", "60min"]

TIMELINE_OPTIONS: list[str] = ["30days", "60days", "90days"]

AGE_RANGES: list[str] = ["16-19", "20-24", "25-29", "30-34", "35-39", "40+"]

CONCERN_OPTIONS: list[str] = [
    "skin",
    "hair",
    "grooming",
    "style",
    "posture",
    "overall",
]

STAGES: dict[str, tuple[int, int]] = {
    "foundation": (1, 7),
    "building": (8, 30),
    "momentum": (31, 60),
    "mastery": (61, 90),
}


def stage_for_day(day: int) -> str:
    """Return the coaching stage name for a given program day."""
    for stage, (start, end) in STAGES.items():
        if start <= day <= end:
            return stage
    return "mastery"
