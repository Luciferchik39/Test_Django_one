"""
Django settings for Django_star project.
"""

import os
from pathlib import Path
import sys

from .config import settings

# BASE_DIR - корень проекта (где manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================
# БЕЗОПАСНОСТЬ
# ============================================
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# ============================================
# ПРИЛОЖЕНИЯ
# ============================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Используем полный путь к приложению
LOCAL_APPS = [
    'apps.my_app',  # ← полный путь от корня проекта
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

# ============================================
# MIDDLEWARE
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.my_app.middleware.RequestLoggingMiddleware',
]

# ============================================
# URL И WSGI
# ============================================
ROOT_URLCONF = 'Django_star.urls'
WSGI_APPLICATION = 'Django_star.wsgi.application'

# ============================================
# ШАБЛОНЫ
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================
# БАЗА ДАННЫХ
# ============================================
if os.environ.get('CI'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'django_star_db'),
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
elif settings.USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': settings.DB_NAME,
            'USER': settings.DB_USER,
            'PASSWORD': settings.DB_PASSWORD,
            'HOST': settings.DB_HOST,
            'PORT': str(settings.DB_PORT),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }

# ============================================
# ВАЛИДАЦИЯ ПАРОЛЕЙ
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# ИНТЕРНАЦИОНАЛИЗАЦИЯ
# ============================================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================
# СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ
# ============================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# ПОЛЕ ПЕРВИЧНОГО КЛЮЧА ПО УМОЛЧАНИЮ
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Loguru настройки
from .logging_config import setup_logging  # noqa: E402

setup_logging()