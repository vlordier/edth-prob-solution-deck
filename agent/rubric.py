"""Judging rubric definitions and scoring math.

Defines the RubricAxis StrEnum, default weighting, and weighted score
computation. Used by triage, candidate ranking, and sub-problem ROI.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum


class RubricAxis(StrEnum):
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
    """Return axis weights as a plain dict from any Mapping."""
    return dict(rubric)


def normalize_weights(weights: Mapping[str, float]) -> dict[str, float]:
    """Normalize weights so they sum to 1.0.

    Raises:
        ValueError: if all weights are zero.
    """
    total = sum(weights.values())
    if total == 0:
        raise ValueError("Cannot normalize: all weights are zero")
    return {k: v / total for k, v in weights.items()}


def score_to_weighted(scores: Mapping[str, float], weights: Mapping[str, float]) -> float:
    """Compute a weighted score given axis scores and rubric weights.

    Raises:
        KeyError: if any required weight axis is missing from scores.
    """
    missing = set(weights.keys()) - set(scores.keys())
    if missing:
        raise KeyError(f"Missing scores for axes: {sorted(missing)}")
    return sum(scores[k] * w for k, w in weights.items())
