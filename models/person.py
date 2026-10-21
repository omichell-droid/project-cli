"""Base Person class shared by anyone who has a name and email."""

from utils.validators import validate_email, validate_name


class Person:
    """A generic person with a validated name and email.

    User inherits from this class, so validation logic lives in one place.
    """

    def __init__(self, name, email=None):
        self.name = name      # goes through the property setter
        self.email = email    # goes through the property setter

    # ----- name -------------------------------------------------------
    @property
    def name(self):
        """The person's display name (non-empty string)."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = validate_name(value)

    # ----- email ------------------------------------------------------
    @property
    def email(self):
        """Optional email address; validated when provided."""
        return self._email

    @email.setter
    def email(self, value):
        self._email = validate_email(value) if value else None

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, email={self.email!r})"
