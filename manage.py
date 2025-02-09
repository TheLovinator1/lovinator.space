#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

from __future__ import annotations

import os
import sys


class DjangoNotInstalledError(ImportError):
    def __init__(self) -> None:
        super().__init__("Couldn't import Django. Verify installation in your environment.")


def main() -> None:
    """Run administrative tasks.

    Raises:
        DjangoNotInstalledError: If Django is not installed.
    """
    os.environ.setdefault(key="DJANGO_SETTINGS_MODULE", value="config.settings")
    try:
        from django.core.management import execute_from_command_line  # noqa: PLC0415

    except ImportError as exc:
        raise DjangoNotInstalledError from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
