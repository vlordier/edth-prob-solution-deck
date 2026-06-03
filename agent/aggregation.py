"""Aggregation algorithms for the panel (Borda, weighted Borda, approval voting)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


def _all_items(rankings: list[dict[str, int]]) -> list[str]:
    seen: list[str] = []
    for r in rankings:
        for k in r:
            if k not in seen:
                seen.append(k)
    return seen


def borda_count(rankings: list[dict[str, int]]) -> list[str]:
    """Rank items by sum of positions across judges (lower = better)."""
    scores: dict[str, float] = defaultdict(lambda: float("inf"))
    for item in _all_items(rankings):
        positions = [r[item] for r in rankings if item in r]
        if positions:
            scores[item] = sum(positions)
    return sorted(scores.keys(), key=lambda k: (scores[k], k))


def weighted_borda(rankings: list[dict[str, int]], weights: Iterable[float]) -> list[str]:
    """Borda count with per-judge weight multipliers.

    Raises:
        ValueError: if weights length does not match rankings length.
    """
    weights = list(weights)
    if len(weights) != len(rankings):
        raise ValueError(
            f"weights length mismatch: got {len(weights)} for {len(rankings)} rankings"
        )
    scores: dict[str, float] = defaultdict(float)
    for item in _all_items(rankings):
        for r, w in zip(rankings, weights, strict=False):
            if item in r:
                scores[item] += r[item] * w
    return sorted(scores.keys(), key=lambda k: (scores[k], k))


def approval_vote(approvals: list[set[str]]) -> list[str]:
    """Rank items by approval count (most approvals first). Ties broken by first-seen order."""
    counts: dict[str, int] = defaultdict(int)
    order: list[str] = []
    for a in approvals:
        for item in a:
            if item not in counts:
                order.append(item)
            counts[item] += 1
    return sorted(counts.keys(), key=lambda k: (-counts[k], order.index(k)))
