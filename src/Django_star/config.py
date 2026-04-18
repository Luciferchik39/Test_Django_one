# src/Django_star/config.py
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings loaded from .env file."""

    # Django Core
    SECRET_KEY: str = 'django-insecure-default-key-change-me'
    DEBUG: bool = True
    ALLOWED_HOSTS: str | list[str] = ['localhost', '127.0.0.1']

    # Database
    USE_POSTGRES: bool = False
    DB_NAME: str = 'django_star_db'
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = ''
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432

    @field_validator('ALLOWED_HOSTS', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Преобразует строку в список, если необходимо."""
        if isinstance(v, str):
            # Если строка в формате JSON
            if v.startswith('['):
                import json
                return json.loads(v)
            # Если обычная строка с запятыми
            return [host.strip() for host in v.split(',')]
        return v

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / '.env'),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )


# Создаём глобальный объект настроек
settings = AppSettings()
