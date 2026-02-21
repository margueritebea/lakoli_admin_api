# src/config/base.py
from pathlib import Path
from datetime import timedelta
import sys
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

SECRET_KEY = os.getenv("SECRET_KEY")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'authentication',
    'administration',
    'communication',
    'finances',
    'library',
    'pedagogie',
    'corsheaders',
]

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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Auth & DRF Config
AUTH_USER_MODEL = 'authentication.User'
AUTHENTICATION_BACKENDS = [
    'apps.authentication.backend.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['apps.authentication.authentication.CookieJWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

# ─── JWT common settings Configuration authentication/servicespy ──────────────────────────────────
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_LIFETIME = timedelta(minutes=30)
JWT_REFRESH_LIFETIME = timedelta(days=7)
JWT_ACCESS_COOKIE = 'access_token'
JWT_REFRESH_COOKIE = 'refresh_token'
JWT_COOKIE_SAMESITE = 'Lax'
JWT_COOKIE_PATH = '/'

CORS_ALLOW_CREDENTIALS = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JWT_SECRET          = SECRET_KEY          #(par défaut)
JWT_COOKIE_SECURE   = not DEBUG          # True en production
JWT_COOKIE_DOMAIN   = None               # ex: '.monecole.gn'






# """
# Configuration de base — partagée par tous les environnements.
# """

# from pathlib import Path
# from datetime import timedelta
# import sys
# import os

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = os.getenv("SECRET_KEY")

# DEBUG = False

# ALLOWED_HOSTS = []

# # ── Applications ──────────────────────────────────────────────────────────────
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',

#     # USER_APPS
#     'core',

#     'authentication',
#     'administration',
#     'communication',
#     'finances',
#     'library',
#     'pedagogie',

#     'corsheaders',
# ]

# # ── Middleware ────────────────────────────────────────────────────────────────
# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'config.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'config.wsgi.application'

# # ── Base de données ───────────────────────────────────────────────────────────
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# # ── Validation des mots de passe ──────────────────────────────────────────────
# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# ]

# # ── Internationalisation ──────────────────────────────────────────────────────
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# # ── Fichiers statiques ────────────────────────────────────────────────────────
# STATIC_URL = 'static/'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # ── Authentification ──────────────────────────────────────────────────────────
# AUTH_USER_MODEL = 'authentication.User'

# AUTHENTICATION_BACKENDS = [
#     'authentication.backend.EmailOrUsernameBackend',
#     'django.contrib.auth.backends.ModelBackend',
# ]

# # ── DRF ───────────────────────────────────────────────────────────────────────
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'authentication.authentication.CookieJWTAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
#     'PAGE_SIZE': 20,
#     'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#     ],
# }

# # ── JWT Cookies ───────────────────────────────────────────────────────────────
# JWT_ALGORITHM        = 'HS256'
# JWT_ACCESS_LIFETIME  = timedelta(minutes=30)
# JWT_REFRESH_LIFETIME = timedelta(days=7)
# JWT_ACCESS_COOKIE    = 'access_token'
# JWT_REFRESH_COOKIE   = 'refresh_token'
# JWT_COOKIE_SECURE    = True
# JWT_COOKIE_SAMESITE  = 'Lax'
# JWT_COOKIE_DOMAIN    = None
# JWT_COOKIE_PATH      = '/'

# # ── CORS ──────────────────────────────────────────────────────────────────────
# CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = []

# # ── CSRF ──────────────────────────────────────────────────────────────────────
# CSRF_COOKIE_HTTPONLY = False
# CSRF_COOKIE_SAMESITE = 'Lax'

# # ── Logging ───────────────────────────────────────────────────────────────────
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {'class': 'logging.StreamHandler'},
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'logs' / 'authentication.log',
#         },
#     },
#     'loggers': {
#         'authentication': {
#             'handlers': ['console', 'file'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#     },
# }