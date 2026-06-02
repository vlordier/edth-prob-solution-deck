"""Tests for agent.rubric."""

from __future__ import annotations

import pytest

from agent.rubric import (
    DEFAULT_RUBRIC,
    RubricAxis,
    get_axis_weights,
    normalize_weights,
    score_to_weighted,
)


def test_default_rubric_has_four_axes() -> None:
    assert set(DEFAULT_RUBRIC.keys()) == {"impact", "innovation", "execution", "presentation"}


def test_default_rubric_weights_sum_to_one() -> None:
    assert abs(sum(DEFAULT_RUBRIC.values()) - 1.0) < 1e-9


def test_rubric_axis_is_string_enum() -> None:
    assert RubricAxis.IMPACT == "impact"
    assert RubricAxis.PRESENTATION == "presentation"


def test_get_axis_weights_returns_dict() -> None:
    assert get_axis_weights(DEFAULT_RUBRIC) == DEFAULT_RUBRIC


def test_normalize_weights_renormalizes_to_one() -> None:
    raw = {"impact": 2.0, "innovation": 1.0, "execution": 1.0, "presentation": 0.0}
    norm = normalize_weights(raw)
    assert abs(sum(norm.values()) - 1.0) < 1e-9
    assert norm["impact"] == pytest.approx(0.5)


def test_score_to_weighted_returns_weighted_average() -> None:
    scores = {"impact": 5, "innovation": 3, "execution": 4, "presentation": 2}
    weights = {"impact": 0.4, "innovation": 0.2, "execution": 0.3, "presentation": 0.1}
    expected = 4.0
    assert score_to_weighted(scores, weights) == pytest.approx(expected)


def test_score_to_weighted_with_missing_axis_raises() -> None:
    with pytest.raises(KeyError):
        score_to_weighted({"impact": 5, "innovation": 3}, DEFAULT_RUBRIC)
