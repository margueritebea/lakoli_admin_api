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

# """
# Configuration de développement.
# Utilisation : DJANGO_SETTINGS_MODULE=config.dev
# """

# from .base import *

# DEBUG = True

# ALLOWED_HOSTS = ['*']

# # ── Cookies non-secure en local (HTTP) ────────────────────────────────────────
# JWT_COOKIE_SECURE = False

# # ── CORS en dev ───────────────────────────────────────────────────────────────
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000',
#     'http://127.0.0.1:3000',
# ]