"""Project model: owned by one User, holds many Tasks."""

from utils.validators import parse_date, validate_name


class Project:
    """A project belonging to a single owner.

    Relationships:
        owner (User) 1 --- * Project
        Project 1 --- * Task
        Project * --- * User via task assignments (contributors)
    """

    _next_id = 1
    _registry = {}

    def __init__(self, title, owner, description="", due_date=None, project_id=None):
        self.title = title
        if self.title.lower() in Project._registry:
            raise ValueError(f"Project '{self.title}' already exists.")
        self.description = description or ""
        self.due_date = due_date
        self.id = project_id if project_id is not None else Project._next_id
        Project._next_id = max(Project._next_id, self.id + 1)
        self.tasks = []             # one-to-many: Project -> Tasks
        self.owner = owner
        owner.add_project(self)
        Project._registry[self.title.lower()] = self

    # ----- properties -------------------------------------------------
    @property
    def title(self):
        """Project title (non-empty, unique)."""
        return self._title

    @title.setter
    def title(self, value):
        self._title = validate_name(value, field="title")

    @property
    def due_date(self):
        """Due date as a datetime.date, or None."""
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        # parse_date accepts strings like "2026-11-30" or "Nov 30 2026".
        self._due_date = parse_date(value) if value else None

    @property
    def contributors(self):
        """Users assigned to at least one task here (many-to-many link)."""
        seen = []
        for task in self.tasks:
            if task.assigned_to and task.assigned_to not in seen:
                seen.append(task.assigned_to)
        return seen

    @property
    def progress(self):
        """Fraction of tasks completed, from 0.0 to 1.0."""
        if not self.tasks:
            return 0.0
        done = sum(1 for t in self.tasks if t.is_complete)
        return done / len(self.tasks)

    # ----- relationships ----------------------------------------------
    def add_task(self, task):
        """Attach a Task to this project (called by Task.__init__)."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task):
        """Detach a Task from this project."""
        if task in self.tasks:
            self.tasks.remove(task)

    # ----- class-level helpers ----------------------------------------
    @classmethod
    def all(cls):
        """Return all projects."""
        return list(cls._registry.values())

    @classmethod
    def find_by_title(cls, title):
        """Return project with this title (case-insensitive) or None."""
        return cls._registry.get(str(title).strip().lower())

    @classmethod
    def search(cls, keyword):
        """Return projects whose title or description contains keyword."""
        kw = keyword.lower()
        return [p for p in cls.all()
                if kw in p.title.lower() or kw in p.description.lower()]

    @classmethod
    def delete(cls, title):
        """Delete a project and its tasks. Returns True if removed."""
        project = cls.find_by_title(title)
        if not project:
            return False
        from models.task import Task
        for task in list(project.tasks):
            Task.delete(task.id)
        project.owner.remove_project(project)
        del cls._registry[project.title.lower()]
        return True

    @classmethod
    def clear(cls):
        """Reset registry and ID counter."""
        cls._registry = {}
        cls._next_id = 1

    # ----- serialization ----------------------------------------------
    def to_dict(self):
        """Convert to a JSON-friendly dict (owner stored by id)."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "owner_id": self.owner.id,
        }

    @classmethod
    def from_dict(cls, data, users_by_id):
        """Rebuild a Project; users_by_id maps id -> User."""
        owner = users_by_id[data["owner_id"]]
        return cls(data["title"], owner, data.get("description", ""),
                   data.get("due_date"), project_id=data.get("id"))

    def __str__(self):
        due = self.due_date.isoformat() if self.due_date else "no due date"
        return (f"[{self.id}] {self.title} (owner: {self.owner.name}, due: {due}, "
                f"{len(self.tasks)} task(s), {self.progress:.0%} done)")
