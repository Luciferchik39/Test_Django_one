FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.3.4 \
    POETRY_HOME="/opt/poetry" \
    DJANGO_SETTINGS_MODULE=config.settings

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Настраиваем Poetry: отключаем виртуальное окружение
# Пакеты будут устанавливаться в системный Python
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости (только основные, без dev)
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Копируем весь проект
COPY . .

# Создаем директории
RUN mkdir -p static media

EXPOSE 8000

# Используем python3 напрямую (уже в PATH)
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]