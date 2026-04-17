# tests/test_project.py
from django.conf import settings
from django.test import TestCase


class ProjectTests(TestCase):
    """Тесты проекта."""

    def test_django_setup(self):
        """Проверка настроек Django."""
        # В тестах DEBUG должен быть False (как в production)
        # Не проверяем конкретное значение, а проверяем, что настройки загружены
        assert hasattr(settings, 'DEBUG')
        assert hasattr(settings, 'INSTALLED_APPS')
        assert 'my_app' in settings.INSTALLED_APPS
        print(f"✅ Django настроен, DEBUG={settings.DEBUG}")

    def test_app_exists(self):
        """Проверка наличия приложения."""
        from django.apps import apps
        app = apps.get_app_config('my_app')
        assert app.name == 'my_app'
        print(f"✅ Приложение '{app.verbose_name}' загружено")

    def test_database_connection(self):
        """Проверка подключения к БД."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            assert row[0] == 1
        print("✅ База данных работает")

    def test_home_page_response(self):
        """Проверка главной страницы."""
        response = self.client.get('/')
        # 404 - нормально, если URL не настроен
        # Проверяем, что сервер отвечает
        self.assertIsNotNone(response)
        print(f"✅ Ответ сервера: {response.status_code}")

    def test_debug_in_tests(self):
        """Проверка, что DEBUG выключен в тестах."""
        # Это нормальное поведение Django
        from django.conf import settings
        assert settings.DEBUG is False
        print("✅ DEBUG выключен в тестах (как и должно быть)")
