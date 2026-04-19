"""
Утилиты для создания логгеров для каждого модуля
"""
from loguru import logger


def get_logger(name: str):
    """
    Создает логгер для конкретного модуля
    Вместо использования корневого логгера

    Пример:
        logger = get_logger(__name__)
        logger.info("Пользователь создан", user_id=123)
    """
    return logger.bind(name=name)


class LoggerMixin:
    """
    Миксин для добавления логгера в классы
    """

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
