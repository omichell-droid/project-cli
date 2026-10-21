"""Shared pytest fixtures."""

import os
import sys

import pytest

# Make the project root importable when running `pytest` from anywhere.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.storage import clear_all  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_registries():
    """Every test starts with empty User/Project/Task registries."""
    clear_all()
    yield
    clear_all()


@pytest.fixture
def data_file(tmp_path):
    """A temporary JSON path so tests never touch data/data.json."""
    return str(tmp_path / "data.json")
