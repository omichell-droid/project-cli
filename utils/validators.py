"""Input validation helpers used by the models."""

import re

from dateutil import parser as date_parser

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_name(value, field="name"):
    """Strip and return value; raise ValueError if it is empty."""
    if value is None or not str(value).strip():
        raise ValueError(f"{field.capitalize()} cannot be empty.")
    return str(value).strip()


def validate_email(value):
    """Return the email lowercased; raise ValueError if malformed."""
    value = str(value).strip().lower()
    if not EMAIL_PATTERN.match(value):
        raise ValueError(f"Invalid email address: '{value}'")
    return value


def parse_date(value):
    """Turn a string (or date) into a datetime.date using python-dateutil.

    Accepts flexible formats such as '2026-11-30', '30/11/2026' or
    'Nov 30 2026'. Raises ValueError for anything it can't understand.
    """
    if hasattr(value, "year") and not isinstance(value, str):
        return value if not hasattr(value, "date") else value.date()
    try:
        return date_parser.parse(str(value), dayfirst=False).date()
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"Could not understand date: '{value}'") from exc
