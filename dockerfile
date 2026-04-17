FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.3.4 \
    POETRY_HOME="/opt/poetry" \
    DJANGO_SETTINGS_MODULE=Django_star.settings \
    PYTHONPATH="/app/src:/app/apps"

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
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости (только основные, без dev)
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Копируем весь проект
COPY . .

# Создаем директории для статики и медиа
RUN mkdir -p static media staticfiles logs

# Собираем статику (опционально)
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Используем gunicorn для production (рекомендуется)
# CMD ["gunicorn", "Django_star.wsgi:application", "--bind", "0.0.0.0:8000"]

# Для разработки используем runserver
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]