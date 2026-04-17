#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
from pathlib import Path
import sys


def main():
    """Run administrative tasks."""
    # Добавляем src в PYTHONPATH
    BASE_DIR = Path(__file__).resolve().parent
    SRC_DIR = BASE_DIR / 'src'

    if SRC_DIR.exists():
        sys.path.insert(0, str(SRC_DIR))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_star.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
