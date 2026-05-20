"""XP thresholds, level calculation, and level names."""

LEVEL_THRESHOLDS: list[int] = [
    0,      # Level 1
    100,    # Level 2
    250,    # Level 3
    500,    # Level 4
    800,    # Level 5
    1200,   # Level 6
    1700,   # Level 7
    2300,   # Level 8
    3000,   # Level 9
    3800,   # Level 10
    4700,   # Level 11
    5700,   # Level 12
    6800,   # Level 13
    8000,   # Level 14
    9500,   # Level 15
    11200,  # Level 16
    13100,  # Level 17
    15200,  # Level 18
    17500,  # Level 19
    20000,  # Level 20
    23000,  # Level 21
    26500,  # Level 22
    30500,  # Level 23
    35000,  # Level 24
    40000,  # Level 25
]

LEVEL_NAMES: dict[int, str] = {
    1: "Beginner",
    2: "Novice",
    3: "Apprentice",
    4: "Dedicated",
    5: "Rising",
    6: "Committed",
    7: "Focused",
    8: "Driven",
    9: "Advanced",
    10: "Established",
    11: "Skilled",
    12: "Proficient",
    13: "Expert",
    14: "Master",
    15: "Elite",
    16: "Champion",
    17: "Legend",
    18: "Titan",
    19: "Mythic",
    20: "Transcendent",
    21: "Ascended",
    22: "Sovereign",
    23: "Immortal",
    24: "Eternal",
    25: "FORGE",
}


def calculate_level(total_xp: int) -> int:
    """Calculate level from total XP."""
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if total_xp >= threshold:
            level = i + 1
        else:
            break
    return min(level, len(LEVEL_THRESHOLDS))


def get_level_name(level: int) -> str:
    """Get the display name for a level."""
    return LEVEL_NAMES.get(level, f"Level {level}")


def xp_for_next_level(total_xp: int) -> dict:
    """Calculate XP progress toward next level."""
    current_level = calculate_level(total_xp)
    if current_level >= len(LEVEL_THRESHOLDS):
        return {
            "current_level": current_level,
            "level_name": get_level_name(current_level),
            "xp_current": total_xp,
            "xp_for_current_level": LEVEL_THRESHOLDS[-1],
            "xp_for_next_level": None,
            "xp_progress": total_xp,
            "xp_needed": 0,
            "progress_pct": 100.0,
        }

    current_threshold = LEVEL_THRESHOLDS[current_level - 1]
    next_threshold = LEVEL_THRESHOLDS[current_level]
    xp_in_level = total_xp - current_threshold
    xp_needed = next_threshold - current_threshold

    return {
        "current_level": current_level,
        "level_name": get_level_name(current_level),
        "xp_current": total_xp,
        "xp_for_current_level": current_threshold,
        "xp_for_next_level": next_threshold,
        "xp_progress": xp_in_level,
        "xp_needed": xp_needed,
        "progress_pct": round((xp_in_level / xp_needed) * 100, 1) if xp_needed > 0 else 100.0,
    }
