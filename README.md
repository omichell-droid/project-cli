# Project Tracker CLI

A command-line project management tool for a team of developers. Admins can create users, give them projects, add tasks to those projects, assign tasks to teammates and mark them complete. All data is saved to a local JSON file.

## Features

- **Users** – create, list and delete users (name + optional email, validated).
- **Projects** – each user owns one or more projects (title, description, due date). List all projects, list one user's projects, search by keyword, edit or delete.
- **Tasks** – each project has one or more tasks (title, status, assigned user). Assign, change status, complete or delete tasks; filter by project, user or status.
- **Relationships**
  - One-to-many: `User → Projects`
  - One-to-many: `Project → Tasks`
  - Many-to-many: `Projects ↔ Users` through task assignments (a project's *contributors*; a user can work on tasks in many projects).
- **Persistence** – everything is saved to `data/data.json`. Missing files start fresh; a corrupt file is backed up to `data.json.bak` instead of being overwritten. Saves are atomic (write to temp file, then rename).
- **Pretty output** – coloured tables and messages using [`rich`](https://pypi.org/project/rich/).
- **Flexible dates** – due dates like `2026-12-01` or `"Dec 1 2026"` are parsed with [`python-dateutil`](https://pypi.org/project/python-dateutil/).

## Project structure

```
project-cli/
├── main.py              # CLI entry point (if __name__ == "__main__")
├── cli/
│   ├── parser.py        # argparse setup – one subcommand per action
│   └── commands.py      # command handlers
├── models/
│   ├── person.py        # Person base class (name/email with validation)
│   ├── user.py          # User(Person) – owns projects
│   ├── project.py       # Project – owned by a user, holds tasks
│   └── task.py          # Task – belongs to a project, assigned to a user
├── utils/
│   ├── storage.py       # JSON load/save with error handling
│   ├── display.py       # rich tables and messages
│   └── validators.py    # name, email and date validation
├── data/data.json       # saved data (sample data included)
├── tests/               # pytest test suite
├── requirements.txt
└── Pipfile
```

## Setup

Requires **Python 3.10+**.

```bash
git clone https://github.com/omichell-droid/project-cli.git
cd project-cli
```

Using pipenv:

```bash
pipenv install --dev
pipenv shell
```

Or using pip and a virtual environment:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

See every command:

```bash
python main.py --help
python main.py add-project --help
```

### Users

```bash
python main.py add-user --name "Alex" --email alex@example.com
python main.py list-users
python main.py delete-user --name "Alex"
```

### Projects

```bash
python main.py add-project --user "Alex" --title "CLI Tool" --description "Tracker app" --due 2026-12-01
python main.py list-projects
python main.py list-projects --user "Alex"
python main.py search-projects tracker
python main.py update-project --title "CLI Tool" --new-title "CLI Tool v2" --due "Dec 15 2026"
python main.py delete-project --title "CLI Tool v2"
```

### Tasks

```bash
python main.py add-task --project "CLI Tool" --title "Implement add-task" --assign "Alex"
python main.py list-tasks
python main.py list-tasks --project "CLI Tool" --status todo
python main.py assign-task --id 1 --user "Sam"
python main.py update-task --id 1 --status in-progress
python main.py complete-task --id 1
python main.py delete-task --id 1
```

Valid statuses: `todo`, `in-progress`, `done`.

### Global options

| Option | Purpose |
| --- | --- |
| `--data PATH` | Use a different JSON file (e.g. `--data data/test.json`) |
| `-v`, `--verbose` | Show debug logging (what was loaded and saved) |

## Running tests

```bash
pytest -v
```

The suite covers the models (validation, relationships, cascading deletes), storage (round-trip, missing and corrupt files) and the CLI end to end. Tests use a temporary data file, so your real `data/data.json` is never touched.

## Known issues / limitations

- Names and project titles must be unique (case-insensitive); task titles may repeat, so tasks are referenced by id.
- A task has a single assignee.
- Data is stored in one JSON file, so it isn't safe for several people editing at the same moment.
- Dates are read month-first when ambiguous (`03/04/2026` = 4 March).
