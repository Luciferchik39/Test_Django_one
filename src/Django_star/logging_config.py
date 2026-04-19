"""
Loguru конфигурация для Django проекта
"""
from pathlib import Path
import sys
import json
from datetime import datetime
from typing import Dict, Any

from django.conf import settings
from loguru import logger


def json_formatter(record: Dict[str, Any]) -> str:
    """
    Форматирует лог в JSON для production окружения
    """
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "process": record["process"].id if record["process"] else None,
        "thread": record["thread"].id if record["thread"] else None,
    }

    # Добавляем exception если есть
    if record["exception"]:
        log_entry["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
            "traceback": record["exception"].traceback,
        }

    # Добавляем дополнительные поля из extra
    extra_fields = {k: v for k, v in record["extra"].items()
                   if k not in ['name', 'function', 'line']}
    if extra_fields:
        log_entry["extra"] = extra_fields

    return json.dumps(log_entry, ensure_ascii=False) + "\n"


def text_formatter(record: Dict[str, Any]) -> str:
    """
    Текстовый формат для разработки
    """
    return "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}\n"


def setup_logging():
    """
    Настройка Loguru с поддержкой JSON формата в production
    """
    # Очищаем стандартные обработчики
    logger.remove()

    # Определяем окружение
    is_production = not settings.DEBUG

    # 1. Консоль (всегда текстовый формат для читаемости)
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        level="INFO" if is_production else "DEBUG",
        colorize=True,
        enqueue=True
    )

    # 2. Директория для логов
    log_dir = Path(settings.BASE_DIR) / 'logs'
    log_dir.mkdir(exist_ok=True)

    # 3. Основной файл логов (разный формат для dev/prod)
    if is_production:
        # Production: JSON формат для машинного чтения
        log_file = log_dir / 'app_{time:YYYY-MM-DD}.json'
        log_format = json_formatter
        log_level = "INFO"
    else:
        # Development: текстовый формат для человека
        log_file = log_dir / 'app_{time:YYYY-MM-DD}.log'
        log_format = text_formatter
        log_level = "DEBUG"

    logger.add(
        log_file,
        format=log_format,
        rotation="100 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
        level=log_level,
        enqueue=True
    )

    # 4. Отдельный файл для ошибок (JSON в production)
    if is_production:
        error_file = log_dir / 'errors_{time:YYYY-MM-DD}.json'
        error_format = json_formatter
    else:
        error_file = log_dir / 'errors_{time:YYYY-MM-DD}.log'
        error_format = text_formatter

    logger.add(
        error_file,
        format=error_format,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        level="ERROR",
        filter=lambda record: record["level"].name == "ERROR",
        enqueue=True
    )

    # 5. Отдельный файл для security логов (всегда JSON)
    logger.add(
        log_dir / 'security_{time:YYYY-MM-DD}.json',
        format=json_formatter,
        rotation="50 MB",
        retention="90 days",
        compression="zip",
        encoding="utf-8",
        level="INFO",
        filter=lambda record: record["extra"].get("type") == "security",
        enqueue=True
    )

    logger.info(f"✅ Loguru настроен (режим: {'PRODUCTION' if is_production else 'DEVELOPMENT'}, формат: {'JSON' if is_production else 'TEXT'})")


# Функция для отправки security логов
def log_security_event(event_type: str, user_id: str = None, details: dict = None):
    """
    Логирование событий безопасности
    """
    logger.bind(type="security").info(
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    )