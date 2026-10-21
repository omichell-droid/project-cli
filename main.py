"""Entry point for the Project Tracker CLI.

Usage examples:
    python main.py add-user --name "Alex" --email alex@example.com
    python main.py add-project --user "Alex" --title "CLI Tool" --due 2026-12-01
    python main.py add-task --project "CLI Tool" --title "Implement add-task" --assign Alex
    python main.py complete-task --id 1
    python main.py --help
"""

import logging
import sys

from cli.commands import CLIError
from cli.parser import build_parser
from utils import display
from utils.storage import DEFAULT_PATH, DataFileError, load_data, save_data


def main(argv=None):
    """Parse arguments, load data, run the command, save if needed.

    Returns a process exit code (0 = success, 1 = error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    path = args.data or DEFAULT_PATH

    try:
        load_data(path)
        changed = args.func(args)
        if changed:
            save_data(path)
        return 0
    except (CLIError, ValueError, DataFileError) as exc:
        display.error(str(exc))
        return 1
    except OSError as exc:
        display.error(f"File problem: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
