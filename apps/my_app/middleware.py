"""
Middleware для логирования HTTP запросов
"""
import time

from src.Django_star.loggers import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware:
    """Middleware для логирования всех HTTP запросов."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Начало обработки запроса
        start_time = time.time()

        # Логируем входящий запрос
        logger.info(
            f"→ {request.method} {request.get_full_path()} "
            f"от {request.user if request.user.is_authenticated else 'Anonymous'}"
        )

        # Обрабатываем запрос
        response = self.get_response(request)

        # Время выполнения
        duration = time.time() - start_time

        # Логируем ответ
        log_level = logger.warning if response.status_code >= 400 else logger.info
        log_level(
            f"← {request.method} {request.get_full_path()} → "
            f"{response.status_code} ({duration:.3f}s)"
        )

        return response
