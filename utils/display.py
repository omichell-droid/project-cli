"""Pretty terminal output built on the `rich` package."""

from rich.console import Console
from rich.table import Table

console = Console()


def success(message):
    """Print a green success message."""
    console.print(f"[bold green]✔[/] {message}")


def error(message):
    """Print a red error message."""
    console.print(f"[bold red]✘ Error:[/] {message}")


def info(message):
    """Print a dim informational message."""
    console.print(f"[dim]{message}[/]")


def users_table(users):
    """Render a table of users."""
    table = Table(title="Users")
    table.add_column("ID", justify="right")
    table.add_column("Name", style="cyan")
    table.add_column("Email")
    table.add_column("Projects", justify="right")
    table.add_column("Tasks assigned", justify="right")
    for u in users:
        table.add_row(str(u.id), u.name, u.email or "-",
                      str(len(u.projects)), str(len(u.assigned_tasks())))
    console.print(table)


def projects_table(projects, title="Projects"):
    """Render a table of projects."""
    table = Table(title=title)
    table.add_column("ID", justify="right")
    table.add_column("Title", style="cyan")
    table.add_column("Owner")
    table.add_column("Due")
    table.add_column("Tasks", justify="right")
    table.add_column("Progress", justify="right")
    table.add_column("Contributors")
    for p in projects:
        table.add_row(
            str(p.id), p.title, p.owner.name,
            p.due_date.isoformat() if p.due_date else "-",
            str(len(p.tasks)), f"{p.progress:.0%}",
            ", ".join(u.name for u in p.contributors) or "-",
        )
    console.print(table)


STATUS_STYLE = {"todo": "yellow", "in-progress": "blue", "done": "green"}


def tasks_table(tasks, title="Tasks"):
    """Render a table of tasks with colour-coded status."""
    table = Table(title=title)
    table.add_column("ID", justify="right")
    table.add_column("Title", style="cyan")
    table.add_column("Project")
    table.add_column("Status")
    table.add_column("Assigned to")
    for t in tasks:
        style = STATUS_STYLE.get(t.status, "white")
        table.add_row(str(t.id), t.title, t.project.title,
                      f"[{style}]{t.status}[/]",
                      t.assigned_to.name if t.assigned_to else "-")
    console.print(table)
