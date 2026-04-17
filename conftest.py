# conftest.py
"""Pytest configuration and fixtures for Django project."""
import os
from pathlib import Path
import sys

# Добавляем пути для корректного импорта (ДОЛЖНО БЫТЬ В НАЧАЛЕ)
BASE_DIR = Path(__file__).resolve().parent

# Добавляем src в PYTHONPATH
src_path = str(BASE_DIR / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Добавляем apps в PYTHONPATH
apps_path = str(BASE_DIR / 'apps')
if apps_path not in sys.path:
    sys.path.insert(0, apps_path)

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_star.settings')

# Теперь можно импортировать Django (noqa: E402 - игнорируем порядок импортов)
import django  # noqa: E402
from django.test import Client  # noqa: E402
import pytest  # noqa: E402

# Инициализируем Django
django.setup()


@pytest.fixture
def client():
    """Django test client fixture."""
    return Client()


@pytest.fixture
def api_client():
    """API client fixture for REST API tests."""
    return Client()


def pytest_configure():
    """Configure pytest markers."""
    pytest.django_db = pytest.mark.django_db
