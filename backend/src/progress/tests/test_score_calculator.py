"""Unit tests for the deterministic score calculator."""

from decimal import Decimal

import pytest

from src.common.constants import PILLARS
from src.progress.score_calculator import (
    apply_seasonal_reweight,
    calculate_optimisation_score,
    clamp,
    derive_initial_weights,
    diff_pillars,
)


class TestDeriveInitialWeights:
    def test_weights_sum_to_one_no_face_shape(self):
        """Equal weights when no face shape provided."""
        weights = derive_initial_weights(face_shape=None, main_concern=None)
        assert abs(sum(weights.values()) - 1.0) < 1e-9

    def test_weights_sum_to_one_with_face_shape(self):
        """Weights still sum to 1.0 after face shape application."""
        for shape in ["oval", "square", "round", "long", "heart", "diamond"]:
            weights = derive_initial_weights(face_shape=shape)
            assert abs(sum(weights.values()) - 1.0) < 1e-9, f"Failed for {shape}"

    def test_face_shape_oval_emphasises_facial_composition(self):
        """Oval face shape gives facial_composition the highest weight."""
        weights = derive_initial_weights(face_shape="oval", season=2)
        assert weights["facial_composition"] > weights["skin"]

    def test_face_shape_square_emphasises_skin_and_style(self):
        """Square face shape boosts skin and style."""
        weights = derive_initial_weights(face_shape="square", season=2)
        assert weights["skin"] > weights["grooming"]
        assert weights["style"] > weights["grooming"]

    def test_face_shape_round_emphasises_grooming_and_hair(self):
        """Round face shape emphasises grooming and hair."""
        weights = derive_initial_weights(face_shape="round", season=2)
        assert weights["grooming"] > weights["facial_composition"]
        assert weights["hair"] > weights["facial_composition"]

    def test_concern_boost_applied(self):
        """Quiz main concern boosts the relevant pillar(s)."""
        weights_no_concern = derive_initial_weights(main_concern=None)
        weights_skin = derive_initial_weights(main_concern="skin")
        assert weights_skin["skin"] > weights_no_concern["skin"]

    def test_concern_boost_posture_also_boosts_style(self):
        """Posture concern boosts both posture and style."""
        weights_base = derive_initial_weights(main_concern=None)
        weights_posture = derive_initial_weights(main_concern="posture")
        assert weights_posture["posture"] > weights_base["posture"]
        assert weights_posture["style"] > weights_base["style"]

    def test_unknown_face_shape_uses_equal_weights(self):
        """Unknown face shape falls back to equal distribution."""
        weights = derive_initial_weights(face_shape="unknown_shape")
        base = 1.0 / len(PILLARS)
        for pillar in PILLARS:
            if pillar != "voice":
                assert abs(weights[pillar] - base) < 0.06

    def test_all_pillars_present(self):
        """All 9 pillars have weights regardless of configuration."""
        weights = derive_initial_weights(face_shape="oval", main_concern="hair")
        for pillar in PILLARS:
            assert pillar in weights


class TestSeasonalReweight:
    def test_season_1_voice_zero(self):
        """Voice weight is 0 in Season 1."""
        weights = derive_initial_weights(season=1)
        assert weights["voice"] == 0.0

    def test_season_2_voice_included(self):
        """Voice gets weight in Season 2+."""
        weights = derive_initial_weights(season=2)
        assert weights["voice"] > 0

    def test_season_2_still_sums_to_one(self):
        """Weights sum to 1.0 after seasonal reweight in Season 2."""
        weights = derive_initial_weights(face_shape="oval", season=2)
        assert abs(sum(weights.values()) - 1.0) < 1e-9

    def test_apply_seasonal_reweight_adds_voice(self):
        """Direct call to apply_seasonal_reweight adds voice in S2."""
        weights = {p: 1.0 / 9 for p in PILLARS}
        weights["voice"] = 0.0
        result = apply_seasonal_reweight(weights, season=2)
        assert result["voice"] == 0.11


class TestCalculateOptimisationScore:
    def test_all_scores_50_returns_50(self):
        """All pillars at 50 with equal weights = 50."""
        scores = {p: 50 for p in PILLARS}
        weights = {p: 1.0 / len(PILLARS) for p in PILLARS}
        result = calculate_optimisation_score(scores, weights)
        assert result == Decimal("50.00")

    def test_weighted_score_correct(self):
        """Weighted average computed correctly with unequal weights."""
        scores = {p: 50 for p in PILLARS}
        weights = {p: 0.1 for p in PILLARS}
        scores["skin"] = 100
        weights["skin"] = 0.5
        result = calculate_optimisation_score(scores, weights)
        assert result > Decimal("50.00")
        assert result < Decimal("100.00")

    def test_null_pillar_excluded(self):
        """Null pillars don't skew the average — excluded from calculation."""
        scores = {p: 80 for p in PILLARS}
        weights = {p: 1.0 / len(PILLARS) for p in PILLARS}
        scores["voice"] = None
        result = calculate_optimisation_score(scores, weights)
        assert result == Decimal("80.00")

    def test_all_null_returns_baseline(self):
        """All-null pillars returns 50 (baseline)."""
        scores = {p: None for p in PILLARS}
        weights = {p: 1.0 / len(PILLARS) for p in PILLARS}
        result = calculate_optimisation_score(scores, weights)
        assert result == Decimal("50.00")

    def test_score_clamped_to_100(self):
        """Score can't exceed 100 even with rounding."""
        scores = {p: 100 for p in PILLARS}
        weights = {p: 1.0 / len(PILLARS) for p in PILLARS}
        result = calculate_optimisation_score(scores, weights)
        assert result <= Decimal("100.00")

    def test_zero_scores_returns_zero(self):
        """All pillars at 0 returns 0."""
        scores = {p: 0 for p in PILLARS}
        weights = {p: 1.0 / len(PILLARS) for p in PILLARS}
        result = calculate_optimisation_score(scores, weights)
        assert result == Decimal("0.00")


class TestDiffPillars:
    def test_positive_diff(self):
        """Positive changes computed correctly."""
        current = {p: 60 for p in PILLARS}
        previous = {p: 50 for p in PILLARS}
        deltas = diff_pillars(current, previous)
        for pillar in PILLARS:
            assert deltas[pillar] == 10

    def test_negative_diff(self):
        """Negative changes computed correctly."""
        current = {p: 40 for p in PILLARS}
        previous = {p: 50 for p in PILLARS}
        deltas = diff_pillars(current, previous)
        for pillar in PILLARS:
            assert deltas[pillar] == -10

    def test_null_returns_none(self):
        """Null in either snapshot produces None delta."""
        current = {p: 60 for p in PILLARS}
        previous = {p: 50 for p in PILLARS}
        current["voice"] = None
        deltas = diff_pillars(current, previous)
        assert deltas["voice"] is None

    def test_diff_clamped(self):
        """Deltas clamped to [-100, 100]."""
        current = {p: 100 for p in PILLARS}
        previous = {p: 0 for p in PILLARS}
        deltas = diff_pillars(current, previous)
        assert all(d == 100 for d in deltas.values())


class TestClamp:
    def test_clamp_below_min(self):
        assert clamp(-5, 0, 100) == 0

    def test_clamp_above_max(self):
        assert clamp(150, 0, 100) == 100

    def test_clamp_within_range(self):
        assert clamp(50, 0, 100) == 50

    def test_clamp_at_boundary(self):
        assert clamp(0, 0, 100) == 0
        assert clamp(100, 0, 100) == 100
