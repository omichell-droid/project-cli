"""Task model: belongs to one Project, optionally assigned to a User."""

from utils.validators import validate_name


class Task:
    """A unit of work inside a project.

    Status is restricted to the values in VALID_STATUSES.
    """

    VALID_STATUSES = ("todo", "in-progress", "done")
    _next_id = 1
    _registry = {}    # keyed by integer id (task titles may repeat across projects)

    def __init__(self, title, project, assigned_to=None, status="todo", task_id=None):
        self.title = title
        self.status = status
        self.assigned_to = assigned_to
        self.id = task_id if task_id is not None else Task._next_id
        Task._next_id = max(Task._next_id, self.id + 1)
        self.project = project
        project.add_task(self)
        Task._registry[self.id] = self

    # ----- properties -------------------------------------------------
    @property
    def title(self):
        """Task title (non-empty)."""
        return self._title

    @title.setter
    def title(self, value):
        self._title = validate_name(value, field="title")

    @property
    def status(self):
        """One of 'todo', 'in-progress', 'done'."""
        return self._status

    @status.setter
    def status(self, value):
        value = str(value).strip().lower()
        if value not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{value}'. Choose from: {', '.join(self.VALID_STATUSES)}")
        self._status = value

    @property
    def is_complete(self):
        """True when status is 'done'."""
        return self.status == "done"

    # ----- behaviour --------------------------------------------------
    def complete(self):
        """Mark this task as done."""
        self.status = "done"

    def assign(self, user):
        """Assign this task to a User (or None to unassign)."""
        self.assigned_to = user

    # ----- class-level helpers ----------------------------------------
    @classmethod
    def all(cls):
        """Return all tasks."""
        return list(cls._registry.values())

    @classmethod
    def find_by_id(cls, task_id):
        """Return the task with this id or None."""
        return cls._registry.get(int(task_id))

    @classmethod
    def delete(cls, task_id):
        """Delete a task by id. Returns True if removed."""
        task = cls.find_by_id(task_id)
        if not task:
            return False
        task.project.remove_task(task)
        del cls._registry[task.id]
        return True

    @classmethod
    def clear(cls):
        """Reset registry and ID counter."""
        cls._registry = {}
        cls._next_id = 1

    # ----- serialization ----------------------------------------------
    def to_dict(self):
        """Convert to a JSON-friendly dict (relations stored by id)."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "project_id": self.project.id,
            "assigned_to_id": self.assigned_to.id if self.assigned_to else None,
        }

    @classmethod
    def from_dict(cls, data, projects_by_id, users_by_id):
        """Rebuild a Task from a dict using id lookup tables."""
        project = projects_by_id[data["project_id"]]
        user = users_by_id.get(data.get("assigned_to_id"))
        return cls(data["title"], project, user, data.get("status", "todo"),
                   task_id=data.get("id"))

    def __str__(self):
        mark = "x" if self.is_complete else " "
        who = self.assigned_to.name if self.assigned_to else "unassigned"
        return f"[{mark}] #{self.id} {self.title} ({self.status}, {who})"
