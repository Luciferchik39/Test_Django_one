"""
Loguru конфигурация для Django проекта
"""
from pathlib import Path
import sys

from django.conf import settings
from loguru import logger


def setup_logging():
    """
    Базовая настройка Loguru

    Основные логи: 7 дней хранения, ротация при 100 MB
    Логи ошибок: 30 дней хранения, ротация при 10 MB
    """
    # Очищаем стандартные обработчики
    logger.remove()

    # 1. Вывод в консоль (с цветами для удобства)
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True
    )

    # 2. Директория для логов
    log_dir = Path(settings.BASE_DIR) / 'logs'
    log_dir.mkdir(exist_ok=True)

    # 3. Основной файл логов (все уровни INFO и выше)
    # Храним 7 дней, ротация при 100 MB (один файл на 7 дней)
    logger.add(
        log_dir / 'app_{time:YYYY-MM-DD}.log',
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="100 MB",     # Ротация при 100 MB
        retention="7 days",    # Храним 7 дней
        compression="zip",     # Сжимаем старые для экономии места
        encoding="utf-8",
        level="INFO"
    )

    # 4. Отдельный файл для ошибок (только ERROR и выше)
    # Храним 30 дней, ротация при 10 MB
    logger.add(
        log_dir / 'errors_{time:YYYY-MM-DD}.log',  # Добавил дату в имя файла
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",      # Ротация при 10 MB
        retention="30 days",   # Храним 30 дней
        compression="zip",     # Сжимаем старые
        encoding="utf-8",
        level="ERROR",
        filter=lambda record: record["level"].name == "ERROR"
    )

    # 5. Опционально: лог для отладки (только при DEBUG=True)
    if settings.DEBUG:
        logger.add(
            log_dir / 'debug.log',
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="1 day",    # Debug логи храним всего 1 день
            compression="zip",
            encoding="utf-8",
            level="DEBUG",
            filter=lambda record: record["level"].name == "DEBUG"
        )

    logger.info("✅ Loguru настроен (основные логи: 7 дней, ошибки: 30 дней)")


# Функция для проверки размера логов (опционально)
def get_logs_size_info():
    """
    Возвращает информацию о размере логов
    """
    log_dir = Path(settings.BASE_DIR) / 'logs'
    if not log_dir.exists():
        return "Логи не найдены"

    total_size: float = 0.0  # ← Явно указываем float
    files_info: list = []  # ← Явно указываем тип list

    for log_file in log_dir.glob("*"):
        if log_file.is_file():
            size_mb = log_file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            files_info.append(f"  {log_file.name}: {size_mb:.2f} MB")

    return f"Общий размер логов: {total_size:.2f} MB\n" + "\n".join(files_info)
