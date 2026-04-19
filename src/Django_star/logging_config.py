"""
Loguru конфигурация для Django проекта
"""
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any

from django.conf import settings
from loguru import logger

# Решаем проблему с Record для Mypy
if TYPE_CHECKING:
    from loguru import Record
else:
    # Рантайм заглушка, чтобы код не падал
    Record = Any


def json_formatter(record: Record) -> str:
    """
    Форматирует лог в JSON для production окружения
    """
    exception = record["exception"]

    payload: dict[str, Any] = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "process": record["process"].id if record["process"] else None,
        "thread": record["thread"].id if record["thread"] else None,
    }

    if exception:
        payload["exception"] = {
            "type": getattr(exception.type, "__name__", str(exception.type)),
            "value": str(exception.value),
            "traceback": bool(exception.traceback),
        }

    extra_fields = {
        k: v for k, v in record["extra"].items()
        if k not in {"name", "function", "line"}
    }
    if extra_fields:
        payload["extra"] = extra_fields

    return json.dumps(payload, ensure_ascii=False) + "\n"


def text_formatter(record: Record) -> str:
    """
    Текстовый формат для разработки
    """
    return "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}\n"


def setup_logging() -> None:
    """
    Настройка Loguru с поддержкой JSON формата в production
    """
    logger.remove()

    is_production = not getattr(settings, "DEBUG", True)
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(exist_ok=True)

    # 1. Консоль
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        level="INFO" if is_production else "DEBUG",
        colorize=True,
        enqueue=True,
    )

    common_opts: dict[str, Any] = {
        "rotation": "100 MB",
        "retention": "7 days",
        "compression": "zip",
        "encoding": "utf-8",
        "enqueue": True,
    }

    # 2. Основной лог
    log_ext = "json" if is_production else "log"
    main_format = json_formatter if is_production else text_formatter

    logger.add(
        log_dir / f"app_{{time:YYYY-MM-DD}}.{log_ext}",
        format=main_format,
        level="INFO" if is_production else "DEBUG",
        **common_opts,
    )

    # 3. Ошибки
    logger.add(
        log_dir / f"errors_{{time:YYYY-MM-DD}}.{log_ext}",
        format=main_format,
        level="ERROR",
        filter=lambda r: r["level"].name == "ERROR",
        **common_opts,
    )

    # 4. Security (Всегда JSON)
    logger.add(
        log_dir / "security_{time:YYYY-MM-DD}.json",
        format=json_formatter,
        level="INFO",
        filter=lambda r: r["extra"].get("type") == "security",
        **common_opts,
    )


def log_security_event(
    event_type: str,
    user_id: str | int | None = None,
    details: dict[str, Any] | None = None
) -> None:
    """
    Логирование событий безопасности
    """
    logger.bind(type="security").info(
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        },
    )
