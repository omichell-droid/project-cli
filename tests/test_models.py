"""Unit tests for User, Project and Task."""

import datetime

import pytest

from models import Person, Project, Task, User


# ----- User / Person ---------------------------------------------------
def test_user_inherits_person():
    user = User("Alex", "alex@example.com")
    assert isinstance(user, Person)
    assert user.email == "alex@example.com"


def test_user_ids_auto_increment():
    a, b = User("A"), User("B")
    assert (a.id, b.id) == (1, 2)


def test_user_name_cannot_be_empty():
    with pytest.raises(ValueError):
        User("   ")


def test_invalid_email_rejected():
    with pytest.raises(ValueError):
        User("Alex", "not-an-email")


def test_duplicate_user_rejected():
    User("Alex")
    with pytest.raises(ValueError):
        User("alex")   # case-insensitive


def test_find_user_case_insensitive():
    user = User("Alex")
    assert User.find_by_name("ALEX") is user
    assert User.find_by_name("nobody") is None


# ----- Project ---------------------------------------------------------
def test_project_links_to_owner():
    user = User("Alex")
    project = Project("CLI Tool", user)
    assert project.owner is user
    assert project in user.projects


def test_project_due_date_parsed():
    project = Project("CLI Tool", User("Alex"), due_date="Dec 1 2026")
    assert project.due_date == datetime.date(2026, 12, 1)


def test_bad_due_date_rejected():
    with pytest.raises(ValueError):
        Project("CLI Tool", User("Alex"), due_date="someday maybe")


def test_project_search_matches_title_and_description():
    user = User("Alex")
    Project("CLI Tool", user, description="argparse app")
    Project("Website", user, description="landing page")
    assert [p.title for p in Project.search("cli")] == ["CLI Tool"]
    assert [p.title for p in Project.search("landing")] == ["Website"]


def test_project_progress_and_contributors():
    alex, sam = User("Alex"), User("Sam")
    project = Project("CLI Tool", alex)
    t1 = Task("One", project, alex)
    Task("Two", project, sam)
    assert project.progress == 0
    t1.complete()
    assert project.progress == 0.5
    assert project.contributors == [alex, sam]


def test_delete_project_removes_tasks():
    user = User("Alex")
    project = Project("CLI Tool", user)
    Task("One", project)
    assert Project.delete("CLI Tool") is True
    assert Task.all() == [] and user.projects == []


# ----- Task ------------------------------------------------------------
def test_task_default_status_and_complete():
    task = Task("Write tests", Project("P", User("A")))
    assert task.status == "todo"
    task.complete()
    assert task.is_complete


def test_task_invalid_status():
    task = Task("Write tests", Project("P", User("A")))
    with pytest.raises(ValueError):
        task.status = "finished"


def test_user_assigned_tasks_span_projects():
    alex, sam = User("Alex"), User("Sam")
    t1 = Task("One", Project("P1", alex), sam)
    t2 = Task("Two", Project("P2", alex), sam)
    assert sam.assigned_tasks() == [t1, t2]


def test_delete_user_cascades_and_unassigns():
    alex, sam = User("Alex"), User("Sam")
    task = Task("Shared", Project("Sam's", sam), alex)
    Project("Alex's", alex)
    User.delete("Alex")
    assert Project.find_by_title("Alex's") is None
    assert task.assigned_to is None


def test_str_output():
    user = User("Alex", "alex@example.com")
    task = Task("Do it", Project("P", user), user)
    assert "Alex" in str(user)
    assert str(task).startswith("[ ] #1 Do it")
