"""System and user prompts for DeepSeek plan generation."""

from src.plans.task_library import TASKS_BY_PILLAR_AND_TIER, LibraryTask

SYSTEM_PROMPT = """\
You are FORGE, a male appearance optimisation coach. You create personalised \
90-day transformation plans.

RULES:
1. Output ONLY valid JSON — no markdown fences, no commentary.
2. Select tasks ONLY from the provided task library IDs.
3. Assign 3-5 tasks per day, covering at least 2 different pillars daily.
4. Spread all 9 pillars across each week, weighted toward the user's goals and concern.
5. Progress from beginner → intermediate → advanced tiers over the 90 days:
   - Weeks 1-4: mostly beginner, some intermediate
   - Weeks 5-9: mostly intermediate, some beginner/advanced
   - Weeks 10-13: mostly intermediate/advanced
6. Each day should take roughly the user's stated daily_time commitment.
7. Reuse tasks across days (routines repeat) but vary within each week.

OUTPUT SCHEMA:
{
  "program_name": "short catchy name for this plan",
  "focus_summary": "1-2 sentence summary of the plan focus",
  "honest_expectation": "1-2 sentence realistic expectation",
  "weeks": [
    {
      "week": 1,
      "days": [
        {
          "day": 1,
          "tasks": [
            {"library_task_id": "skin-b-01", "pillar": "skin", "tier": "beginner"},
            ...
          ]
        },
        ...7 days
      ]
    },
    ...13 weeks
  ]
}
"""


def build_user_prompt(
    goals: list[str],
    routine_level: str,
    daily_time: str,
    timeline: str,
    main_concern: str,
    age_range: str,
    has_photo: bool,
    available_tasks: dict[tuple[str, str], list[LibraryTask]] | None = None,
) -> str:
    """Build the user message with quiz context and available task IDs."""
    if available_tasks is None:
        available_tasks = TASKS_BY_PILLAR_AND_TIER

    task_catalog = _format_task_catalog(available_tasks)

    return f"""\
USER PROFILE:
- Goals: {", ".join(goals)}
- Current routine level: {routine_level}
- Daily time available: {daily_time}
- Timeline: {timeline}
- Main concern: {main_concern}
- Age range: {age_range}
- Has baseline photo: {has_photo}

AVAILABLE TASK LIBRARY:
{task_catalog}

Generate a complete 90-day (13-week) plan using ONLY the task IDs listed above. \
Output raw JSON matching the schema described in the system prompt.\
"""


def _format_task_catalog(
    tasks: dict[tuple[str, str], list[LibraryTask]],
) -> str:
    """Format the task library into a compact catalog string for the prompt."""
    lines: list[str] = []
    for (pillar, tier), task_list in sorted(tasks.items()):
        lines.append(f"\n## {pillar} / {tier}")
        for t in task_list:
            lines.append(f"  {t.id}: {t.title} ({t.duration_mins}min, {t.xp_value}xp)")
    return "\n".join(lines)
