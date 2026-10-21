"""Builds the argparse parser with one subcommand per action."""

import argparse

from cli import commands
from models import Task


def build_parser():
    """Return the configured ArgumentParser."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Project Tracker - manage users, projects and tasks from the command line.",
    )
    parser.add_argument("--data", help="Path to the JSON data file (default: data/data.json)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logging")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # --- users ---
    p = sub.add_parser("add-user", help="Create a new user")
    p.add_argument("--name", required=True, help="User's name (unique)")
    p.add_argument("--email", help="User's email address")
    p.set_defaults(func=commands.add_user)

    p = sub.add_parser("list-users", help="List all users")
    p.set_defaults(func=commands.list_users)

    p = sub.add_parser("delete-user", help="Delete a user and their projects")
    p.add_argument("--name", required=True)
    p.set_defaults(func=commands.delete_user)

    # --- projects ---
    p = sub.add_parser("add-project", help="Create a project for a user")
    p.add_argument("--user", required=True, help="Owner's name")
    p.add_argument("--title", required=True, help="Project title (unique)")
    p.add_argument("--description", default="", help="Short description")
    p.add_argument("--due", help="Due date, e.g. 2026-12-01 or 'Dec 1 2026'")
    p.set_defaults(func=commands.add_project)

    p = sub.add_parser("list-projects", help="List projects (optionally for one user)")
    p.add_argument("--user", help="Only show projects owned by this user")
    p.set_defaults(func=commands.list_projects)

    p = sub.add_parser("search-projects", help="Search projects by keyword")
    p.add_argument("keyword", help="Text to look for in title or description")
    p.set_defaults(func=commands.search_projects)

    p = sub.add_parser("update-project", help="Edit a project's details")
    p.add_argument("--title", required=True, help="Current project title")
    p.add_argument("--new-title", help="New title")
    p.add_argument("--description", help="New description")
    p.add_argument("--due", help="New due date")
    p.set_defaults(func=commands.update_project)

    p = sub.add_parser("delete-project", help="Delete a project and its tasks")
    p.add_argument("--title", required=True)
    p.set_defaults(func=commands.delete_project)

    # --- tasks ---
    p = sub.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", required=True, help="Project title")
    p.add_argument("--title", required=True, help="Task title")
    p.add_argument("--assign", help="Name of the user to assign it to")
    p.set_defaults(func=commands.add_task)

    p = sub.add_parser("list-tasks", help="List tasks with optional filters")
    p.add_argument("--project", help="Filter by project title")
    p.add_argument("--user", help="Filter by assigned user")
    p.add_argument("--status", choices=Task.VALID_STATUSES, help="Filter by status")
    p.set_defaults(func=commands.list_tasks)

    p = sub.add_parser("assign-task", help="Assign a task to a user")
    p.add_argument("--id", type=int, required=True, help="Task id")
    p.add_argument("--user", required=True, help="User name")
    p.set_defaults(func=commands.assign_task)

    p = sub.add_parser("update-task", help="Change a task's status")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--status", required=True, choices=Task.VALID_STATUSES)
    p.set_defaults(func=commands.update_task)

    p = sub.add_parser("complete-task", help="Mark a task as done")
    p.add_argument("--id", type=int, required=True, help="Task id")
    p.set_defaults(func=commands.complete_task)

    p = sub.add_parser("delete-task", help="Delete a task")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=commands.delete_task)

    return parser
