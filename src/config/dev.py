# src/config/dev.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

JWT_COOKIE_SECURE = False

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]