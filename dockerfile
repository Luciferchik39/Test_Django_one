# ============================================
# СТАДИЯ 1: Установка Poetry (отдельный слой)
# ============================================
FROM python:3.12-slim AS poetry-builder

ENV POETRY_VERSION=2.3.4 \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION


# ============================================
# СТАДИЯ 2: Сборка зависимостей (builder)
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Копируем Poetry из предыдущей стадии
COPY --from=poetry-builder /opt/poetry /opt/poetry
ENV PATH="/opt/poetry/bin:$PATH"

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \

    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости в виртуальное окружение (только main)
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --only main --no-root


# ============================================
# СТАДИЯ 3: Финальный образ (runner)
# ============================================
FROM python:3.12-slim AS runner

# Аргументы для версионирования
ARG APP_VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF

# Метаданные образа
LABEL maintainer="Ilya <ilya@ops.com>" \
      version="${APP_VERSION}" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}" \
      description="Django_star - Book Store Application"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=Django_star.settings \
    PYTHONPATH="/app/src:/app/apps" \
    APP_VERSION=${APP_VERSION}

WORKDIR /app

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение из builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Копируем код проекта
COPY . .

# Создаем директории для статики и медиа
RUN mkdir -p static media staticfiles logs

# Создаём непривилегированного пользователя для безопасности
RUN addgroup --system django && \
    adduser --system --group django && \
    chown -R django:django /app

# Переключаемся на непривилегированного пользователя
USER django

EXPOSE 8000

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Для разработки используем runserver
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Для production используйте gunicorn (раскомментируйте ниже)
# CMD ["gunicorn", "Django_star.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]