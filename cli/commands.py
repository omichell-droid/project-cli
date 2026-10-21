"""Command handlers. Each takes the parsed argparse namespace and returns
True if data changed (so main can save), and raises CLIError on bad input."""

from models import Project, Task, User
from utils import display


class CLIError(Exception):
    """A user-facing error (unknown user, bad id, etc.)."""


# ----- lookup helpers --------------------------------------------------
def _get_user(name):
    """Find a user by name or raise a friendly CLIError."""
    user = User.find_by_name(name)
    if not user:
        raise CLIError(f"No user named '{name}'. Run `list-users` to see users.")
    return user


def _get_project(title):
    """Find a project by title or raise a friendly CLIError."""
    project = Project.find_by_title(title)
    if not project:
        raise CLIError(f"No project titled '{title}'. Run `list-projects` to see projects.")
    return project


def _get_task(task_id):
    """Find a task by id or raise a friendly CLIError."""
    task = Task.find_by_id(task_id)
    if not task:
        raise CLIError(f"No task with id {task_id}. Run `list-tasks` to see tasks.")
    return task


# ----- users -----------------------------------------------------------
def add_user(args):
    """add-user --name NAME [--email EMAIL]"""
    user = User(args.name, args.email)
    display.success(f"Created user {user.name} (id {user.id}).")
    return True


def list_users(args):
    """list-users"""
    users = User.all()
    if not users:
        display.info("No users yet. Add one with `add-user --name NAME`.")
    else:
        display.users_table(users)
    return False


def delete_user(args):
    """delete-user --name NAME (also deletes their projects)"""
    user = _get_user(args.name)
    User.delete(user.name)
    display.success(f"Deleted user {user.name} and their projects.")
    return True


# ----- projects --------------------------------------------------------
def add_project(args):
    """add-project --user NAME --title TITLE [--description] [--due]"""
    owner = _get_user(args.user)
    project = Project(args.title, owner, args.description, args.due)
    display.success(f"Created project '{project.title}' for {owner.name}.")
    return True


def list_projects(args):
    """list-projects [--user NAME]"""
    if args.user:
        user = _get_user(args.user)
        projects, title = user.projects, f"Projects owned by {user.name}"
    else:
        projects, title = Project.all(), "All projects"
    if not projects:
        display.info("No projects found.")
    else:
        display.projects_table(projects, title)
    return False


def search_projects(args):
    """search-projects KEYWORD"""
    results = Project.search(args.keyword)
    if not results:
        display.info(f"No projects match '{args.keyword}'.")
    else:
        display.projects_table(results, f"Projects matching '{args.keyword}'")
    return False


def update_project(args):
    """update-project --title TITLE [--new-title] [--description] [--due]"""
    project = _get_project(args.title)
    if not any([args.new_title, args.description is not None, args.due]):
        raise CLIError("Nothing to update. Pass --new-title, --description or --due.")
    if args.new_title:
        if Project.find_by_title(args.new_title):
            raise CLIError(f"A project titled '{args.new_title}' already exists.")
        # Re-key the registry under the new title.
        del Project._registry[project.title.lower()]
        project.title = args.new_title
        Project._registry[project.title.lower()] = project
    if args.description is not None:
        project.description = args.description
    if args.due:
        project.due_date = args.due
    display.success(f"Updated project '{project.title}'.")
    return True


def delete_project(args):
    """delete-project --title TITLE"""
    project = _get_project(args.title)
    Project.delete(project.title)
    display.success(f"Deleted project '{project.title}' and its tasks.")
    return True


# ----- tasks -----------------------------------------------------------
def add_task(args):
    """add-task --project TITLE --title TITLE [--assign NAME]"""
    project = _get_project(args.project)
    assignee = _get_user(args.assign) if args.assign else None
    task = Task(args.title, project, assignee)
    display.success(f"Added task #{task.id} '{task.title}' to '{project.title}'.")
    return True


def list_tasks(args):
    """list-tasks [--project TITLE] [--user NAME] [--status STATUS]"""
    tasks = Task.all()
    if args.project:
        tasks = [t for t in tasks if t.project is _get_project(args.project)]
    if args.user:
        tasks = [t for t in tasks if t.assigned_to is _get_user(args.user)]
    if args.status:
        tasks = [t for t in tasks if t.status == args.status]
    if not tasks:
        display.info("No tasks found.")
    else:
        display.tasks_table(tasks)
    return False


def assign_task(args):
    """assign-task --id ID --user NAME"""
    task = _get_task(args.id)
    user = _get_user(args.user)
    task.assign(user)
    display.success(f"Assigned task #{task.id} to {user.name}.")
    return True


def update_task(args):
    """update-task --id ID --status STATUS"""
    task = _get_task(args.id)
    task.status = args.status
    display.success(f"Task #{task.id} is now '{task.status}'.")
    return True


def complete_task(args):
    """complete-task --id ID"""
    task = _get_task(args.id)
    if task.is_complete:
        display.info(f"Task #{task.id} was already complete.")
        return False
    task.complete()
    display.success(f"Marked task #{task.id} '{task.title}' as done.")
    return True


def delete_task(args):
    """delete-task --id ID"""
    task = _get_task(args.id)
    Task.delete(task.id)
    display.success(f"Deleted task #{task.id}.")
    return True
