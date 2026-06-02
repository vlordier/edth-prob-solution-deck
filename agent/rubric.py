"""Judging rubric definitions and scoring math."""

from __future__ import annotations

from enum import Enum
from typing import Mapping


class RubricAxis(str, Enum):
    IMPACT = "impact"
    INNOVATION = "innovation"
    EXECUTION = "execution"
    PRESENTATION = "presentation"


DEFAULT_RUBRIC: dict[str, float] = {
    RubricAxis.IMPACT.value: 0.30,
    RubricAxis.INNOVATION.value: 0.25,
    RubricAxis.EXECUTION.value: 0.25,
    RubricAxis.PRESENTATION.value: 0.20,
}


def get_axis_weights(rubric: Mapping[str, float]) -> dict[str, float]:
    return dict(rubric)


def normalize_weights(weights: Mapping[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total == 0:
        raise ValueError("Cannot normalize: all weights are zero")
    return {k: v / total for k, v in weights.items()}


def score_to_weighted(
    scores: Mapping[str, float], weights: Mapping[str, float]
) -> float:
    missing = set(weights.keys()) - set(scores.keys())
    if missing:
        raise KeyError(f"Missing scores for axes: {sorted(missing)}")
    return sum(scores[k] * w for k, w in weights.items())
