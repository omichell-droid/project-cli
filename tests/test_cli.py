"""End-to-end tests that drive main() exactly like the terminal would."""

import pytest

from main import main
from models import Project, Task, User
from utils.storage import load_data


def run(data_file, *args):
    """Run a CLI command against the temp data file; return exit code."""
    return main(["--data", data_file, *args])


def test_full_workflow(data_file, capsys):
    assert run(data_file, "add-user", "--name", "Alex", "--email", "alex@example.com") == 0
    assert run(data_file, "add-project", "--user", "Alex", "--title", "CLI Tool") == 0
    assert run(data_file, "add-task", "--project", "CLI Tool",
               "--title", "Implement add-task", "--assign", "Alex") == 0
    assert run(data_file, "complete-task", "--id", "1") == 0

    load_data(data_file)   # read back what the CLI saved
    task = Task.find_by_id(1)
    assert task.is_complete and task.assigned_to.name == "Alex"
    assert Project.find_by_title("CLI Tool").owner.name == "Alex"


def test_list_projects_for_user(data_file, capsys):
    run(data_file, "add-user", "--name", "Alex")
    run(data_file, "add-user", "--name", "Sam")
    run(data_file, "add-project", "--user", "Alex", "--title", "Alpha")
    run(data_file, "add-project", "--user", "Sam", "--title", "Beta")
    capsys.readouterr()
    run(data_file, "list-projects", "--user", "Alex")
    out = capsys.readouterr().out
    assert "Alpha" in out and "Beta" not in out


def test_search_projects(data_file, capsys):
    run(data_file, "add-user", "--name", "Alex")
    run(data_file, "add-project", "--user", "Alex", "--title", "Website",
        "--description", "marketing landing page")
    capsys.readouterr()
    run(data_file, "search-projects", "landing")
    assert "Website" in capsys.readouterr().out


def test_update_project(data_file):
    run(data_file, "add-user", "--name", "Alex")
    run(data_file, "add-project", "--user", "Alex", "--title", "Old")
    assert run(data_file, "update-project", "--title", "Old",
               "--new-title", "New", "--due", "2026-12-25") == 0
    load_data(data_file)
    assert Project.find_by_title("Old") is None
    assert Project.find_by_title("New").due_date.isoformat() == "2026-12-25"


def test_unknown_user_gives_error(data_file, capsys):
    code = run(data_file, "add-project", "--user", "Ghost", "--title", "X")
    assert code == 1
    assert "No user named 'Ghost'" in capsys.readouterr().out


def test_bad_task_id_gives_error(data_file, capsys):
    assert run(data_file, "complete-task", "--id", "99") == 1
    assert "No task with id 99" in capsys.readouterr().out


def test_duplicate_user_gives_error(data_file):
    run(data_file, "add-user", "--name", "Alex")
    assert run(data_file, "add-user", "--name", "alex") == 1


def test_missing_required_argument_exits():
    with pytest.raises(SystemExit):
        main(["add-user"])          # --name is required


def test_status_filter(data_file, capsys):
    run(data_file, "add-user", "--name", "Alex")
    run(data_file, "add-project", "--user", "Alex", "--title", "P")
    run(data_file, "add-task", "--project", "P", "--title", "Done one")
    run(data_file, "add-task", "--project", "P", "--title", "Open one")
    run(data_file, "complete-task", "--id", "1")
    capsys.readouterr()
    run(data_file, "list-tasks", "--status", "done")
    out = capsys.readouterr().out
    assert "Done one" in out and "Open one" not in out


def test_read_only_commands_do_not_create_file(data_file):
    import os
    run(data_file, "list-users")
    assert not os.path.exists(data_file)
    assert User.all() == []
