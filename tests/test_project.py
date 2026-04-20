# tests/test_project.py
from django.conf import settings
from django.test import TestCase
from django.apps import apps


class ProjectTests(TestCase):
    """Тесты проекта."""

    def test_django_setup(self):
        """Проверка настроек Django."""
        self.assertTrue(hasattr(settings, 'DEBUG'))
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        # Используем 'my_app' (без apps.) для проверки
        self.assertIn('apps.my_app', settings.INSTALLED_APPS)
        print(f"✅ Django настроен, DEBUG={settings.DEBUG}")

    def test_app_exists(self):
        app = apps.get_app_config('my_app')
        # Проверяем, что имя совпадает с путем в INSTALLED_APPS
        self.assertEqual(app.name, 'apps.my_app')
        print(f"✅ Приложение '{app.verbose_name}' загружено")

    def test_database_connection(self):
        """Проверка подключения к БД."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            self.assertEqual(row[0], 1)
        print("✅ База данных работает")

    def test_home_page_response(self):
        """Проверка главной страницы."""
        from django.urls import reverse
        response = self.client.get(reverse('my_app:home'))
        self.assertEqual(response.status_code, 200)
        print(f"✅ Главная страница доступна")

    def test_debug_in_tests(self):
        """Проверка, что DEBUG выключен в тестах."""
        self.assertFalse(settings.DEBUG)
        print("✅ DEBUG выключен в тестах")