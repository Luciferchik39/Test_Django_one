# ===============================
# Настройки проекта
# ===============================
PY_SRCS = config manage.py

.PHONY: help install lint fmt type security cc mi check run test

help:
	@echo "📋 Доступные команды:"
	@echo "  make install   - Установка зависимостей"
	@echo "  make lint      - Ruff check (стиль кода)"
	@echo "  make fmt       - Ruff format (форматирование)"
	@echo "  make type      - Mypy (проверка типов)"
	@echo "  make security  - Bandit (безопасность)"
	@echo "  make cc        - Radon (сложность кода)"
	@echo "  make check     - Все проверки вместе"
	@echo "  make run       - Запуск Django сервера"
	@echo "  make test      - Запуск pytest"

install:
	poetry install

lint:
	poetry run ruff check . --fix

fmt:
	poetry run ruff format .

type:
	poetry run mypy .

security:
	poetry run bandit -r config manage.py -s B311,B324

cc:
	poetry run radon cc config manage.py -s -a

check: lint type security cc
	@echo ""
	@echo "✅ Все проверки пройдены успешно!"
	@echo "🎉 Код соответствует стандартам качества"

run:
	poetry run python manage.py runserver

test:
	poetry run pytest
