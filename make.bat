@echo off
REM Используем Python из виртуального окружения
set VENV=.venv
set PYTHON=%VENV%\Scripts\python.exe
set POETRY_RUN=%PYTHON% -m poetry run

if "%1"=="" (
    echo Available commands:
    echo   make install   - Install dependencies
    echo   make lint      - Ruff check
    echo   make fmt       - Ruff format
    echo   make type      - Mypy type check
    echo   make security  - Bandit security
    echo   make cc        - Radon complexity
    echo   make check     - Run all checks
    echo   make run       - Run Django server
    echo   make test      - Run pytest
    exit /b
)

if "%1"=="install" %PYTHON% -m poetry install
if "%1"=="lint" %POETRY_RUN% ruff check . --fix
if "%1"=="fmt" %POETRY_RUN% ruff format .
if "%1"=="type" %POETRY_RUN% mypy .
if "%1"=="security" %POETRY_RUN% bandit -r config manage.py -s B311,B324
if "%1"=="cc" %POETRY_RUN% radon cc config manage.py -s -a
if "%1"=="check" (
    echo Running lint...
    %POETRY_RUN% ruff check . --fix
    echo Running type check...
    %POETRY_RUN% mypy .
    echo Running security check...
    %POETRY_RUN% bandit -r config manage.py -s B311,B324
    echo Running complexity analysis...
    %POETRY_RUN% radon cc config manage.py -s -a
    echo.
    echo All checks passed!
)
if "%1"=="run" %PYTHON% manage.py runserver
if "%1"=="test" %POETRY_RUN% pytest
if "%1"=="docker-build" docker build -t django-app .
if "%1"=="docker-run" docker run -p 8000:8000 --env-file .env django-app
if "%1"=="docker-compose-up" docker-compose up
if "%1"=="docker-compose-down" docker-compose down

# .\make check для запуска проверко по этому файлу