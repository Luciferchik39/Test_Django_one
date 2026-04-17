# src/Django_star/config.py
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings loaded from .env file."""

    # Django Core (с явными значениями по умолчанию)
    SECRET_KEY: str = 'django-insecure-default-key-change-me'
    DEBUG: bool = True
    ALLOWED_HOSTS: list[str] = ['localhost', '127.0.0.1']

    # Database
    USE_POSTGRES: bool = False
    DB_NAME: str = 'django_star_db'
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = ''
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / '.env'),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )


# Создаём глобальный объект настроек
settings = AppSettings()
