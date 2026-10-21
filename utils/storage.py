"""Load and save all models to a single JSON file."""

import json
import logging
import os
import shutil

from models import Project, Task, User

logger = logging.getLogger(__name__)

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "data.json")


def clear_all():
    """Empty every model registry (used before loading and in tests)."""
    Task.clear()
    Project.clear()
    User.clear()


def load_data(path=DEFAULT_PATH):
    """Read the JSON file and rebuild User, Project and Task objects.

    - Missing file: start with empty data.
    - Malformed JSON: back the bad file up to <path>.bak and start empty,
      so the user's data is never silently destroyed.
    """
    clear_all()
    if not os.path.exists(path):
        logger.info("No data file at %s; starting fresh.", path)
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        users = {u["id"]: User.from_dict(u) for u in raw.get("users", [])}
        projects = {p["id"]: Project.from_dict(p, users) for p in raw.get("projects", [])}
        for t in raw.get("tasks", []):
            Task.from_dict(t, projects, users)
        logger.debug("Loaded %d users, %d projects, %d tasks",
                     len(users), len(projects), len(Task.all()))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        backup = path + ".bak"
        shutil.copy(path, backup)
        clear_all()
        logger.warning("Data file was corrupt (%s). Backed up to %s.", exc, backup)
        raise DataFileError(f"Data file is corrupt; a backup was saved to {backup}.") from exc


def save_data(path=DEFAULT_PATH):
    """Write every object to JSON. Writes to a temp file first, then
    renames it, so a crash mid-write can't leave a half-written file."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload = {
        "users": [u.to_dict() for u in User.all()],
        "projects": [p.to_dict() for p in Project.all()],
        "tasks": [t.to_dict() for t in Task.all()],
    }
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, path)
        logger.debug("Saved data to %s", path)
    except OSError as exc:
        logger.error("Could not save data: %s", exc)
        raise


class DataFileError(Exception):
    """Raised when the data file exists but cannot be parsed."""
