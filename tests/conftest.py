"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_artefacts_dir(tmp_path: Path) -> Path:
    """A fresh artefacts/ directory in a tmp location."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    return artefacts
