"""User model: a Person who owns projects (one-to-many)."""

from models.person import Person


class User(Person):
    """A team member who can own projects and be assigned tasks.

    Class attributes:
        _next_id: auto-incrementing ID counter shared by all users.
        _registry: every User created, keyed by lowercase name.
    """

    _next_id = 1
    _registry = {}

    def __init__(self, name, email=None, user_id=None):
        super().__init__(name, email)
        if self.name.lower() in User._registry:
            raise ValueError(f"User '{self.name}' already exists.")
        # Use the stored id when loading from file, otherwise generate one.
        self.id = user_id if user_id is not None else User._next_id
        User._next_id = max(User._next_id, self.id + 1)
        self.projects = []          # one-to-many: User -> Projects
        User._registry[self.name.lower()] = self

    # ----- relationships ----------------------------------------------
    def add_project(self, project):
        """Attach a Project to this user (called by Project.__init__)."""
        if project not in self.projects:
            self.projects.append(project)

    def remove_project(self, project):
        """Detach a Project from this user."""
        if project in self.projects:
            self.projects.remove(project)

    def assigned_tasks(self):
        """Return every task (across all projects) assigned to this user."""
        from models.task import Task
        return [t for t in Task.all() if t.assigned_to is self]

    # ----- class-level collection helpers -----------------------------
    @classmethod
    def all(cls):
        """Return all users as a list."""
        return list(cls._registry.values())

    @classmethod
    def find_by_name(cls, name):
        """Return the user with this name (case-insensitive) or None."""
        return cls._registry.get(str(name).strip().lower())

    @classmethod
    def delete(cls, name):
        """Remove a user and all their projects. Returns True if removed."""
        user = cls.find_by_name(name)
        if not user:
            return False
        from models.project import Project
        for project in list(user.projects):
            Project.delete(project.title)
        # Unassign any tasks this user was working on in other projects.
        for task in user.assigned_tasks():
            task.assigned_to = None
        del cls._registry[user.name.lower()]
        return True

    @classmethod
    def clear(cls):
        """Reset the registry and ID counter (used by tests and loading)."""
        cls._registry = {}
        cls._next_id = 1

    # ----- serialization ----------------------------------------------
    def to_dict(self):
        """Convert to a JSON-friendly dict."""
        return {"id": self.id, "name": self.name, "email": self.email}

    @classmethod
    def from_dict(cls, data):
        """Rebuild a User from a dict produced by to_dict()."""
        return cls(data["name"], data.get("email"), user_id=data.get("id"))

    def __str__(self):
        email = f" <{self.email}>" if self.email else ""
        return f"[{self.id}] {self.name}{email} - {len(self.projects)} project(s)"
