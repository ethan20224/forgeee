"""Unit tests for the deterministic score estimator — no DB required."""

from src.quiz.estimator import (
    compute_optimisation_score,
    determine_tier,
    estimate_scores,
    full_estimate,
)


def test_all_pillars_returned():
    scores = estimate_scores(
        goals=["skin"],
        routine_level="basic",
        daily_time="20min",
        main_concern="overall",
        age_range="25-29",
        has_photo=False,
    )
    assert len(scores) == 9
    assert all(0 <= v <= 100 for v in scores.values())


def test_scores_clamped_to_bounds():
    scores = estimate_scores(
        goals=[],
        routine_level="none",
        daily_time="10min",
        main_concern="skin",
        age_range="40+",
        has_photo=False,
    )
    assert all(0 <= v <= 100 for v in scores.values())


def test_advanced_routine_higher_than_none():
    adv = estimate_scores(
        goals=["skin"],
        routine_level="advanced",
        daily_time="30min",
        main_concern="overall",
        age_range="25-29",
        has_photo=True,
    )
    none = estimate_scores(
        goals=["skin"],
        routine_level="none",
        daily_time="30min",
        main_concern="overall",
        age_range="25-29",
        has_photo=True,
    )
    assert sum(adv.values()) > sum(none.values())


def test_photo_bonus_applied():
    with_photo = estimate_scores(
        goals=[],
        routine_level="basic",
        daily_time="20min",
        main_concern="overall",
        age_range="25-29",
        has_photo=True,
    )
    without = estimate_scores(
        goals=[],
        routine_level="basic",
        daily_time="20min",
        main_concern="overall",
        age_range="25-29",
        has_photo=False,
    )
    assert all(with_photo[p] >= without[p] for p in with_photo)


def test_concern_penalty():
    scores = estimate_scores(
        goals=["skin", "hair"],
        routine_level="moderate",
        daily_time="30min",
        main_concern="skin",
        age_range="25-29",
        has_photo=False,
    )
    assert scores["skin"] < scores["hair"]


def test_age_affects_skin_and_hair():
    young = estimate_scores(
        goals=[],
        routine_level="basic",
        daily_time="20min",
        main_concern="overall",
        age_range="16-19",
        has_photo=False,
    )
    older = estimate_scores(
        goals=[],
        routine_level="basic",
        daily_time="20min",
        main_concern="overall",
        age_range="40+",
        has_photo=False,
    )
    assert young["skin"] > older["skin"]
    assert young["hair"] > older["hair"]
    assert young["posture"] == older["posture"]


def test_goal_boost():
    with_goals = estimate_scores(
        goals=["posture", "voice"],
        routine_level="basic",
        daily_time="20min",
        main_concern="overall",
        age_range="25-29",
        has_photo=False,
    )
    without = estimate_scores(
        goals=[],
        routine_level="basic",
        daily_time="20min",
        main_concern="overall",
        age_range="25-29",
        has_photo=False,
    )
    assert with_goals["posture"] > without["posture"]
    assert with_goals["voice"] > without["voice"]
    assert with_goals["skin"] == without["skin"]


def test_compute_optimisation_score():
    scores = {"a": 60, "b": 40}
    assert compute_optimisation_score(scores) == 50.0


def test_compute_optimisation_empty():
    assert compute_optimisation_score({}) == 50.0


def test_determine_tier_boundaries():
    assert determine_tier(70) == "advanced"
    assert determine_tier(69.9) == "intermediate"
    assert determine_tier(45) == "intermediate"
    assert determine_tier(44.9) == "beginner"
    assert determine_tier(0) == "beginner"
    assert determine_tier(100) == "advanced"


def test_full_estimate_structure():
    result = full_estimate(
        goals=["skin", "hair"],
        routine_level="moderate",
        daily_time="30min",
        main_concern="skin",
        age_range="25-29",
        has_photo=True,
    )
    assert "pillar_scores" in result
    assert len(result["pillar_scores"]) == 9
    assert "optimisation_score" in result
    assert "tier" in result
    assert "summary" in result
    for p in result["pillar_scores"]:
        assert "pillar" in p
        assert "score" in p
        assert "label" in p
