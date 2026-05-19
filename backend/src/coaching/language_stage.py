"""Language stage logic for coaching content.

The coaching engine uses three language stages that evolve as the user progresses:
- outcome (days 1-14): Focus on visible results and quick wins
- habit (days 15-30): Focus on routine building and consistency
- mechanism (days 31+): Focus on the science and mechanisms behind improvements
"""

LANGUAGE_STAGES: dict[str, tuple[int, int]] = {
    "outcome": (1, 14),
    "habit": (15, 30),
    "mechanism": (31, 90),
}


def stage_for_day(program_day: int) -> str:
    """Determine the coaching language stage for a given program day."""
    for stage, (start, end) in LANGUAGE_STAGES.items():
        if start <= program_day <= end:
            return stage
    return "mechanism"


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Maps program_day to a coaching language stage (outcome/habit/mechanism).

Flow:
1. stage_for_day() checks which range the day falls into
2. Returns stage name used for template selection

Main Entry Point: stage_for_day

Dependencies: None
"""
