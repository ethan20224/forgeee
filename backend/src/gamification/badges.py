"""Badge catalog — defines all unlockable achievements and their conditions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BadgeDefinition:
    badge_id: str
    name: str
    description: str
    icon: str
    category: str
    condition_type: str
    threshold: int


BADGE_CATALOG: dict[str, BadgeDefinition] = {
    # Streak milestones
    "streak_3": BadgeDefinition(
        badge_id="streak_3",
        name="First Flame",
        description="Complete a 3-day streak",
        icon="flame",
        category="streak",
        condition_type="streak",
        threshold=3,
    ),
    "streak_7": BadgeDefinition(
        badge_id="streak_7",
        name="Week Warrior",
        description="Complete a 7-day streak",
        icon="flame",
        category="streak",
        condition_type="streak",
        threshold=7,
    ),
    "streak_14": BadgeDefinition(
        badge_id="streak_14",
        name="Fortnight Force",
        description="Complete a 14-day streak",
        icon="flame",
        category="streak",
        condition_type="streak",
        threshold=14,
    ),
    "streak_30": BadgeDefinition(
        badge_id="streak_30",
        name="Monthly Machine",
        description="Complete a 30-day streak",
        icon="flame",
        category="streak",
        condition_type="streak",
        threshold=30,
    ),
    "streak_60": BadgeDefinition(
        badge_id="streak_60",
        name="Iron Will",
        description="Complete a 60-day streak",
        icon="flame",
        category="streak",
        condition_type="streak",
        threshold=60,
    ),
    "streak_90": BadgeDefinition(
        badge_id="streak_90",
        name="Unstoppable",
        description="Complete a 90-day streak",
        icon="trophy",
        category="streak",
        condition_type="streak",
        threshold=90,
    ),
    # Task milestones
    "tasks_10": BadgeDefinition(
        badge_id="tasks_10",
        name="Getting Started",
        description="Complete 10 tasks",
        icon="checkmark-circle",
        category="tasks",
        condition_type="tasks_completed",
        threshold=10,
    ),
    "tasks_50": BadgeDefinition(
        badge_id="tasks_50",
        name="Committed",
        description="Complete 50 tasks",
        icon="checkmark-circle",
        category="tasks",
        condition_type="tasks_completed",
        threshold=50,
    ),
    "tasks_100": BadgeDefinition(
        badge_id="tasks_100",
        name="Centurion",
        description="Complete 100 tasks",
        icon="checkmark-circle",
        category="tasks",
        condition_type="tasks_completed",
        threshold=100,
    ),
    "tasks_250": BadgeDefinition(
        badge_id="tasks_250",
        name="Dedicated",
        description="Complete 250 tasks",
        icon="star",
        category="tasks",
        condition_type="tasks_completed",
        threshold=250,
    ),
    "tasks_500": BadgeDefinition(
        badge_id="tasks_500",
        name="Legend",
        description="Complete 500 tasks",
        icon="star",
        category="tasks",
        condition_type="tasks_completed",
        threshold=500,
    ),
    # XP / Level milestones
    "level_5": BadgeDefinition(
        badge_id="level_5",
        name="Rising",
        description="Reach Level 5",
        icon="trending-up",
        category="level",
        condition_type="level",
        threshold=5,
    ),
    "level_10": BadgeDefinition(
        badge_id="level_10",
        name="Established",
        description="Reach Level 10",
        icon="trending-up",
        category="level",
        condition_type="level",
        threshold=10,
    ),
    "level_20": BadgeDefinition(
        badge_id="level_20",
        name="Elite",
        description="Reach Level 20",
        icon="medal",
        category="level",
        condition_type="level",
        threshold=20,
    ),
    # Cycle milestones
    "cycle_1": BadgeDefinition(
        badge_id="cycle_1",
        name="First Scan",
        description="Complete your first cycle check-in",
        icon="camera",
        category="cycles",
        condition_type="cycles_completed",
        threshold=1,
    ),
    "cycle_5": BadgeDefinition(
        badge_id="cycle_5",
        name="Tracker",
        description="Complete 5 cycle check-ins",
        icon="camera",
        category="cycles",
        condition_type="cycles_completed",
        threshold=5,
    ),
    "cycle_10": BadgeDefinition(
        badge_id="cycle_10",
        name="Visual Historian",
        description="Complete 10 cycle check-ins",
        icon="camera",
        category="cycles",
        condition_type="cycles_completed",
        threshold=10,
    ),
    # Score milestones
    "score_60": BadgeDefinition(
        badge_id="score_60",
        name="Above Average",
        description="Reach an optimisation score of 60",
        icon="analytics",
        category="score",
        condition_type="optimisation_score",
        threshold=60,
    ),
    "score_70": BadgeDefinition(
        badge_id="score_70",
        name="High Performer",
        description="Reach an optimisation score of 70",
        icon="analytics",
        category="score",
        condition_type="optimisation_score",
        threshold=70,
    ),
    "score_80": BadgeDefinition(
        badge_id="score_80",
        name="Top Tier",
        description="Reach an optimisation score of 80",
        icon="analytics",
        category="score",
        condition_type="optimisation_score",
        threshold=80,
    ),
    # Season completion
    "season_1": BadgeDefinition(
        badge_id="season_1",
        name="Season 1 Complete",
        description="Complete your first 90-day season",
        icon="ribbon",
        category="season",
        condition_type="season_completed",
        threshold=1,
    ),
    "season_2": BadgeDefinition(
        badge_id="season_2",
        name="Season 2 Complete",
        description="Complete two full seasons",
        icon="ribbon",
        category="season",
        condition_type="season_completed",
        threshold=2,
    ),
}

STREAK_BADGE_IDS = [b.badge_id for b in BADGE_CATALOG.values() if b.condition_type == "streak"]


def get_badges_for_condition(condition_type: str, value: int) -> list[BadgeDefinition]:
    """Return all badges that should be unlocked for a given condition/value."""
    return [
        b for b in BADGE_CATALOG.values()
        if b.condition_type == condition_type and b.threshold <= value
    ]
