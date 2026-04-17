@echo off
REM Используем Python из виртуального окружения
set VENV=.venv
set PYTHON=%VENV%\Scripts\python.exe
set POETRY_RUN=%PYTHON% -m poetry run

if "%1"=="" (
    echo Available commands:
    echo   make install        - Install dependencies
    echo   make lint           - Ruff check
    echo   make fmt            - Ruff format
    echo   make type           - Mypy type check
    echo   make security       - Bandit security
    echo   make cc             - Radon complexity
    echo   make check          - Run all checks
    echo   make run            - Run Django server
    echo   make test           - Run pytest
    echo   make migrate        - Run Django migrations
    echo   make shell          - Django shell
    echo   make docker-build   - Build Docker image
    echo   make docker-run     - Run Docker container
    echo   make docker-up      - Docker compose up
    echo   make docker-down    - Docker compose down
    exit /b
)

if "%1"=="install" %PYTHON% -m poetry install
if "%1"=="lint" %POETRY_RUN% ruff check . --fix
if "%1"=="fmt" %POETRY_RUN% ruff format .
if "%1"=="type" %POETRY_RUN% mypy src/ apps/ manage.py
if "%1"=="security" %POETRY_RUN% bandit -r src/ apps/ manage.py -s B311,B324
if "%1"=="cc" %POETRY_RUN% radon cc src/ apps/ manage.py -s -a
if "%1"=="check" (
    echo Running lint...
    %POETRY_RUN% ruff check . --fix
    echo.
    echo Running type check...
    %POETRY_RUN% mypy src/ apps/ manage.py
    echo.
    echo Running security check...
    %POETRY_RUN% bandit -r src/ apps/ manage.py -s B311,B324
    echo.
    echo Running complexity analysis...
    %POETRY_RUN% radon cc src/ apps/ manage.py -s -a
    echo.
    echo All checks passed!
)
if "%1"=="run" %PYTHON% manage.py runserver
if "%1"=="test" %POETRY_RUN% pytest
if "%1"=="migrate" %PYTHON% manage.py migrate
if "%1"=="shell" %PYTHON% manage.py shell
if "%1"=="docker-build" docker build -t django-app .
if "%1"=="docker-run" docker run -p 8000:8000 --env-file .env django-app
if "%1"=="docker-up" docker-compose up -d
if "%1"=="docker-down" docker-compose down

# .\make check для запуска проверко по этому файлу