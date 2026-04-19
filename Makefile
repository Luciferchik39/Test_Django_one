# Makefile для Django_star проекта
# Работает на Windows и Linux, а также внутри Docker контейнера

.PHONY: help install lint fmt type security cc check run test migrate shell docker-build docker-run docker-up docker-down

# Определяем окружение
ifeq ($(INSIDE_CONTAINER),true)
    # Внутри контейнера: poetry установлен глобально
    POETRY_RUN := poetry run
    PYTHON := python
else
    # На хосте: используем .venv
    VENV := .venv
    ifeq ($(OS),Windows_NT)
        PYTHON := $(VENV)/Scripts/python.exe
    else
        PYTHON := $(VENV)/bin/python
    endif
    POETRY_RUN := $(PYTHON) -m poetry run
endif

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make lint           - Ruff check"
	@echo "  make fmt            - Ruff format"
	@echo "  make type           - Mypy type check"
	@echo "  make security       - Bandit security"
	@echo "  make cc             - Radon complexity"
	@echo "  make check          - Run all checks"
	@echo "  make run            - Run Django server"
	@echo "  make test           - Run pytest"
	@echo "  make migrate        - Run Django migrations"
	@echo "  make shell          - Django shell"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make docker-up      - Docker compose up"
	@echo "  make docker-down    - Docker compose down"

install:
	$(POETRY_RUN) install

lint:
	$(POETRY_RUN) ruff check . --fix

fmt:
	$(POETRY_RUN) ruff format .

type:
	$(POETRY_RUN) mypy src/ apps/ manage.py

security:
	$(POETRY_RUN) bandit -r src/ apps/ manage.py -s B311,B324

cc:
	$(POETRY_RUN) radon cc src/ apps/ manage.py -s -a

check:
	@echo "Running lint..."
	$(POETRY_RUN) ruff check . --fix
	@echo ""
	@echo "Running type check..."
	$(POETRY_RUN) mypy src/ apps/ manage.py
	@echo ""
	@echo "Running security check..."
	$(POETRY_RUN) bandit -r src/ apps/ manage.py -s B311,B324
	@echo ""
	@echo "Running complexity analysis..."
	$(POETRY_RUN) radon cc src/ apps/ manage.py -s -a
	@echo ""
	@echo "✅ All checks passed!"

run:
	python manage.py runserver

test:
	$(POETRY_RUN) pytest -v

migrate:
	python manage.py migrate

shell:
	python manage.py shell

docker-build:
	docker build -t django_star:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env django_star:latest

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down