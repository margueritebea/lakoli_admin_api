# src/config/base.py
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
import sys
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True

# ─────────────────────────────────────────────────────
# Applications
# ─────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # TIERS_APPS
    'corsheaders',

    # USER_APPS
    'core',
    'authentication',
    'administration',
    'communication',
    'finances',
    'library',
    'pedagogie',
]

# ─────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ─────────────────────────────────────────────────────
# Templates (OBLIGATOIRE pour admin)
# ─────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────
# Validation mots de passe
# ─────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────────────
# Auth personnalisée
# ─────────────────────────────────────────────────────
AUTH_USER_MODEL = 'authentication.User'
AUTHENTICATION_BACKENDS = [
    'apps.authentication.backend.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ─────────────────────────────────────────────────────
# DRF
# ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.authentication.authentication.CookieJWTAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer'
    ],
}

# ─────────────────────────────────────────────────────
# JWT
# ─────────────────────────────────────────────────────
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_LIFETIME = timedelta(minutes=30)
JWT_REFRESH_LIFETIME = timedelta(days=7)
JWT_ACCESS_COOKIE = 'access_token'
JWT_REFRESH_COOKIE = 'refresh_token'
JWT_COOKIE_SAMESITE = 'Lax'
JWT_COOKIE_PATH = '/'
JWT_SECRET = SECRET_KEY
JWT_COOKIE_SECURE = not DEBUG
JWT_COOKIE_DOMAIN = None

# ─────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────
CORS_ALLOW_CREDENTIALS = True

# ─────────────────────────────────────────────────────
# Internationalisation
# ─────────────────────────────────────────────────────
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────
# Static
# ─────────────────────────────────────────────────────
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

