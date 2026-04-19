#!/usr/bin/env python
"""Скрипт для проверки и отображения структуры проекта."""

from datetime import datetime
from pathlib import Path
from typing import Any


class StructureChecker:
    """Класс для проверки структуры проекта."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.ignore_dirs = {
            '.venv', 'venv', '__pycache__', '.git', '.pytest_cache',
            '.ruff_cache', 'mypy_cache', '.idea', '.mypy_cache',
            'logs', 'staticfiles', 'media'
        }
        self.ignore_files = {
            'db.sqlite3', '.DS_Store', 'Thumbs.db', 'poetry.lock'
        }
        self.structure_lines = []

    def should_ignore_dir(self, dir_name: str) -> bool:
        """Проверяет, нужно ли игнорировать директорию."""
        return dir_name in self.ignore_dirs or dir_name.startswith('.')

    def should_ignore_file(self, file_name: str) -> bool:
        """Проверяет, нужно ли игнорировать файл."""
        return file_name in self.ignore_files or file_name.endswith(('.pyc', '.pyo'))

    def format_size(self, size: int) -> str:
        """Форматирует размер файла."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def collect_structure(self, path: Path = None, prefix: str = "", level: int = 0, max_level: int = 4):
        """Рекурсивный сбор структуры."""
        if path is None:
            path = self.root_path
            self.structure_lines.append(f"📁 {path.name}/")
            prefix = "    "

        if level > max_level:
            return

        try:
            items = []
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    if not self.should_ignore_dir(item.name):
                        items.append(item)
                else:
                    if not self.should_ignore_file(item.name) and \
                            (item.suffix in ['.py', '.toml', '.md', '.env', '.yaml', '.yml', '.ini', '.bat'] or
                             item.name == 'manage.py'):
                        items.append(item)

            for i, item in enumerate(items):
                is_last = (i == len(items) - 1)
                connector = "└── " if is_last else "├── "

                if item.is_dir():
                    self.structure_lines.append(f"{prefix}{connector}{item.name}/")
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    self.collect_structure(item, next_prefix, level + 1, max_level)
                else:
                    size = item.stat().st_size
                    size_str = self.format_size(size)
                    self.structure_lines.append(f"{prefix}{connector}{item.name} ({size_str})")

        except PermissionError:
            self.structure_lines.append(f"{prefix}    ⚠️ Permission denied")

    def count_items(self) -> dict[str, int]:
        """Подсчитывает количество файлов и директорий."""
        files_count = 0
        dirs_count = 0

        for line in self.structure_lines:
            if line.strip().startswith('📁'):
                dirs_count += 1
            elif ' (' in line and not line.strip().startswith('📁'):
                files_count += 1

        return {'files': files_count, 'dirs': dirs_count}

    def save_to_file(self, output_file: Path):
        """Сохраняет структуру в файл."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("СТРУКТУРА ПРОЕКТА\n")
            f.write(f"Путь: {self.root_path}\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write("\n".join(self.structure_lines))
            f.write("\n\n" + "=" * 80 + "\n")

            stats = self.count_items()
            f.write("СТАТИСТИКА:\n")
            f.write(f"  Всего директорий: {stats['dirs']}\n")
            f.write(f"  Всего файлов: {stats['files']}\n")
            f.write("=" * 80 + "\n")

    def print_structure(self, max_lines: int = 50):
        """Выводит структуру в консоль."""
        print("\n".join(self.structure_lines[:max_lines]))
        if len(self.structure_lines) > max_lines:
            print(f"\n... и еще {len(self.structure_lines) - max_lines} строк")


class ProjectValidator:
    """Валидатор структуры проекта."""

    def __init__(self, root_path: Path):
        self.root_path = root_path

    def validate(self) -> dict[str, Any]:
        """Проверяет наличие необходимых файлов и директорий."""
        result = {
            'required_dirs': {},
            'required_files': {},
            'app_structure': {},
            'issues': []
        }

        # Проверка обязательных директорий
        required_dirs = {
            'src/Django_star': self.root_path / 'src' / 'Django_star',
            'apps': self.root_path / 'apps',
            'tests': self.root_path / 'tests',
            'static': self.root_path / 'static',
            'media': self.root_path / 'media',
        }

        for name, path in required_dirs.items():
            result['required_dirs'][name] = path.exists()
            if not path.exists():
                result['issues'].append(f"❌ Отсутствует директория: {name}")

        # Проверка обязательных файлов
        required_files = {
            'manage.py': self.root_path / 'manage.py',
            'pyproject.toml': self.root_path / 'pyproject.toml',
            'pytest.ini': self.root_path / 'pytest.ini',
            'conftest.py': self.root_path / 'conftest.py',
            '.env': self.root_path / '.env',
            'src/Django_star/settings.py': self.root_path / 'src' / 'Django_star' / 'settings.py',
            'src/Django_star/urls.py': self.root_path / 'src' / 'Django_star' / 'urls.py',
        }

        for name, path in required_files.items():
            result['required_files'][name] = path.exists()
            if not path.exists():
                result['issues'].append(f"❌ Отсутствует файл: {name}")

        # Проверка структуры приложения
        app_path = self.root_path / 'apps' / 'my_app'
        if app_path.exists():
            app_files = ['__init__.py', 'models.py', 'views.py', 'admin.py', 'apps.py']
            for file in app_files:
                result['app_structure'][file] = (app_path / file).exists()

        return result

    def print_report(self, result: dict[str, Any]):
        """Выводит отчет о валидации."""
        print("\n" + "=" * 60)
        print("ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
        print("=" * 60)

        print("\n📁 Обязательные директории:")
        for name, exists in result['required_dirs'].items():
            status = "✅" if exists else "❌"
            print(f"  {status} {name}")

        print("\n📄 Обязательные файлы:")
        for name, exists in result['required_files'].items():
            status = "✅" if exists else "❌"
            print(f"  {status} {name}")

        if result['app_structure']:
            print("\n📦 Структура приложения (apps/my_app/):")
            for name, exists in result['app_structure'].items():
                status = "✅" if exists else "❌"
                print(f"  {status} {name}")

        if result['issues']:
            print("\n⚠️ Проблемы:")
            for issue in result['issues']:
                print(f"  {issue}")
        else:
            print("\n✅ Все проверки пройдены успешно!")

        print("=" * 60)


def main():
    """Основная функция."""
    project_path = Path.cwd()

    print("🔍 Анализ структуры проекта...")
    print(f"📁 Текущая директория: {project_path}\n")

    # 1. Сбор структуры
    checker = StructureChecker(project_path)
    checker.collect_structure()
    checker.print_structure()

    # 2. Сохранение в файл
    output_file = project_path / 'project_structure.txt'
    checker.save_to_file(output_file)
    print(f"\n📄 Полная структура сохранена в: {output_file}")

    # 3. Валидация
    validator = ProjectValidator(project_path)
    validation_result = validator.validate()
    validator.print_report(validation_result)

    # 4. Статистика
    stats = checker.count_items()
    print("\n📊 Статистика:")
    print(f"  📁 Директорий: {stats['dirs']}")
    print(f"  📄 Файлов: {stats['files']}")

    # 5. Дополнительная информация
    print("\n💡 Полезные команды:")
    print("  poetry run python manage.py check  - Проверка Django")
    print("  poetry run pytest -v               - Запуск тестов")
    print("  .\\make.bat check                  - Все проверки")
    print("  poetry run python manage.py runserver - Запуск сервера")


if __name__ == '__main__':
    main()
