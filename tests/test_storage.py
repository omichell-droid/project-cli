"""Tests for JSON save/load, including error handling."""

import json
import os

import pytest

from models import Project, Task, User
from utils.storage import DataFileError, load_data, save_data


def test_round_trip(data_file):
    alex = User("Alex", "alex@example.com")
    project = Project("CLI Tool", alex, "desc", "2026-12-01")
    Task("Build parser", project, alex, "in-progress")
    save_data(data_file)

    load_data(data_file)   # clears registries, then rebuilds
    alex2 = User.find_by_name("Alex")
    project2 = Project.find_by_title("CLI Tool")
    assert alex2 is not alex                 # fresh objects
    assert project2.owner is alex2           # relationship restored
    assert project2.tasks[0].assigned_to is alex2
    assert project2.tasks[0].status == "in-progress"
    assert project2.due_date.isoformat() == "2026-12-01"


def test_ids_continue_after_load(data_file):
    User("A"), User("B")
    save_data(data_file)
    load_data(data_file)
    assert User("C").id == 3


def test_missing_file_starts_empty(data_file):
    load_data(data_file)
    assert User.all() == []


def test_corrupt_file_is_backed_up(data_file):
    with open(data_file, "w") as f:
        f.write("{ this is not json")
    with pytest.raises(DataFileError):
        load_data(data_file)
    assert os.path.exists(data_file + ".bak")
    assert User.all() == []


def test_saved_file_is_valid_json(data_file):
    User("Alex")
    save_data(data_file)
    with open(data_file) as f:
        data = json.load(f)
    assert data["users"][0]["name"] == "Alex"
    assert set(data) == {"users", "projects", "tasks"}
