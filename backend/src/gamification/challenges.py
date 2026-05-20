"""Challenge templates — time-limited goals that award bonus XP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChallengeTemplate:
    challenge_id: str
    name: str
    description: str
    icon: str
    target: int
    duration_days: int
    xp_reward: int
    condition_type: str
    pillar: str | None = None


CHALLENGE_CATALOG: list[ChallengeTemplate] = [
    ChallengeTemplate(
        challenge_id="streak_7_challenge",
        name="7-Day Streak",
        description="Maintain a 7-day completion streak",
        icon="flame",
        target=7,
        duration_days=10,
        xp_reward=50,
        condition_type="streak",
    ),
    ChallengeTemplate(
        challenge_id="skin_week",
        name="Skin Focus Week",
        description="Complete 5 skin tasks this week",
        icon="sparkles",
        target=5,
        duration_days=7,
        xp_reward=30,
        condition_type="pillar_tasks",
        pillar="skin",
    ),
    ChallengeTemplate(
        challenge_id="grooming_week",
        name="Grooming Blitz",
        description="Complete 5 grooming tasks this week",
        icon="cut",
        target=5,
        duration_days=7,
        xp_reward=30,
        condition_type="pillar_tasks",
        pillar="grooming",
    ),
    ChallengeTemplate(
        challenge_id="hair_week",
        name="Hair Care Sprint",
        description="Complete 5 hair tasks this week",
        icon="brush",
        target=5,
        duration_days=7,
        xp_reward=30,
        condition_type="pillar_tasks",
        pillar="hair",
    ),
    ChallengeTemplate(
        challenge_id="posture_week",
        name="Posture Power",
        description="Complete 5 posture tasks this week",
        icon="body",
        target=5,
        duration_days=7,
        xp_reward=30,
        condition_type="pillar_tasks",
        pillar="posture",
    ),
    ChallengeTemplate(
        challenge_id="perfect_day",
        name="Perfect Day",
        description="Complete all tasks in a single day",
        icon="star",
        target=1,
        duration_days=3,
        xp_reward=25,
        condition_type="perfect_day",
    ),
    ChallengeTemplate(
        challenge_id="tasks_20_week",
        name="Task Machine",
        description="Complete 20 tasks in one week",
        icon="checkmark-done",
        target=20,
        duration_days=7,
        xp_reward=40,
        condition_type="tasks_in_period",
    ),
    ChallengeTemplate(
        challenge_id="cycle_checkin",
        name="Visual Progress",
        description="Complete a cycle check-in",
        icon="camera",
        target=1,
        duration_days=14,
        xp_reward=20,
        condition_type="cycle_completed",
    ),
    ChallengeTemplate(
        challenge_id="early_bird",
        name="Early Bird",
        description="Complete 3 tasks before 9am",
        icon="sunny",
        target=3,
        duration_days=7,
        xp_reward=25,
        condition_type="early_tasks",
    ),
    ChallengeTemplate(
        challenge_id="full_week",
        name="Full Week",
        description="Complete tasks every day for 7 days",
        icon="calendar",
        target=7,
        duration_days=7,
        xp_reward=35,
        condition_type="streak",
    ),
]


def get_available_challenges(
    active_ids: set[str],
    completed_ids: set[str],
    max_active: int = 3,
) -> list[ChallengeTemplate]:
    """Return challenges eligible to be started (not active and not completed)."""
    available = [
        c for c in CHALLENGE_CATALOG
        if c.challenge_id not in active_ids and c.challenge_id not in completed_ids
    ]
    return available[:max_active]
