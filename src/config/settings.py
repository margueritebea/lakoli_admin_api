from .base import *
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    'api.votre-ecole.com,localhost'
).split(',')

# ─────────────────────────────────────────────────────
# Database PostgreSQL
# ─────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'school_db'),
        'USER': os.getenv('DB_USER', 'school_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'secure_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ─────────────────────────────────────────────────────
# Celery
# ─────────────────────────────────────────────────────
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = os.getenv('TIME_ZONE', 'Africa/Conakry')

# ─────────────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────────────
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# ─────────────────────────────────────────────────────
# Internationalisation
# ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

# ─────────────────────────────────────────────────────
# Sécurité production
# ─────────────────────────────────────────────────────
JWT_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

# ─────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'production.log',
        },
    },
    'loggers': {
        'authentication': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
# from .base import *
# import os

# # Base Settings
# DEBUG = os.getenv('DEBUG', 'False') == 'True'
# ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'api.votre-ecole.com,localhost').split(',')

# # ── Database (PostgreSQL) ──────────────────────────────────────────────────
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
#         'NAME': os.getenv('DB_NAME', 'school_db'),
#         'USER': os.getenv('DB_USER', 'school_user'),
#         'PASSWORD': os.getenv('DB_PASSWORD', 'secure_password'),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', '5432'),
#     }
# }

# # ── Redis & Celery ─────────────────────────────────────────────────────────
# CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
# CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = os.getenv('TIME_ZONE', 'Africa/Conakry')

# # ── Storage (AWS S3) ───────────────────────────────────────────────────────
# USE_S3 = os.getenv('USE_S3', 'False') == 'True'

# if USE_S3:
#     INSTALLED_APPS += ['storages']
#     AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
#     AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
#     AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-west-1')
#     AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    
#     # Files config
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# # ── Email ──────────────────────────────────────────────────────────────────
# EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# # ── Sécurité & Internationalisation ────────────────────────────────────────
# # LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'fr')
# # TIME_ZONE = os.getenv('TIME_ZONE', 'Africa/Conakry')

# # Internationalization
# # https://docs.djangoproject.com/en/6.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True


# JWT_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
# CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

# # ── Logging ────────────────────────────────────────────────────────────────
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'logs' / 'production.log',
#         },
#     },
#     'loggers': {
#         'authentication': {
#             'handlers': ['file'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#     },
# }




























# """
# Django settings for config project.

# Generated by 'django-admin startproject' using Django 6.0.2.

# For more information on this file, see
# https://docs.djangoproject.com/en/6.0/topics/settings/

# For the full list of settings and their values, see
# https://docs.djangoproject.com/en/6.0/ref/settings/
# """

# from pathlib import Path
# from datetime import timedelta

# import sys
# import os

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent


# # Quick-start development settings - unsuitable for production
# # See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.getenv("SECRET_KEY")

# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# ALLOWED_HOSTS = []


# # Application definition

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

# ]


# MIDDLEWARE = [
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


# # Database
# # https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# # Password validation
# # https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# # Internationalization
# # https://docs.djangoproject.com/en/6.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

# USE_I18N = True

# USE_TZ = True


# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/6.0/howto/static-files/

# STATIC_URL = 'static/'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# # ── Authentification ──────────────────────────────────────────────────────────
# AUTH_USER_MODEL = 'authentication.User'

# AUTHENTICATION_BACKENDS = [
#     'apps.authentication.backend.EmailOrUsernameBackend',
#     'django.contrib.auth.backends.ModelBackend',
# ]



# # ── DRF ───────────────────────────────────────────────────────────────────────
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'apps.authentication.authentication.CookieJWTAuthentication',
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
# JWT_ALGORITHM       = 'HS256'
# JWT_ACCESS_LIFETIME  = timedelta(minutes=30)
# JWT_REFRESH_LIFETIME = timedelta(days=7)
# JWT_ACCESS_COOKIE    = 'access_token'
# JWT_REFRESH_COOKIE   = 'refresh_token'
# JWT_COOKIE_SECURE    = not DEBUG          # True en production (HTTPS obligatoire)
# JWT_COOKIE_SAMESITE  = 'Lax'             # 'Strict' si même domaine uniquement
# JWT_COOKIE_DOMAIN    = None              # ex: '.monecole.gn' pour sous-domaines
# JWT_COOKIE_PATH      = '/'

# # ── CORS (si frontend séparé) ─────────────────────────────────────────────────
# # pip install django-cors-headers
# INSTALLED_APPS += ['corsheaders']
# MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000',    # React/Next.js dev
#     'https://monecole.gn',      # Production
# ]
# CORS_ALLOW_CREDENTIALS = True   # OBLIGATOIRE pour envoyer les cookies cross-origin

# # ── CSRF ─────────────────────────────────────────────────────────────────────
# # Pour les APIs cookie-based, le CSRF doit être géré côté frontend.
# # Option 1 : Activer le middleware CSRF (recommandé, le frontend doit envoyer csrftoken)
# # CSRF_COOKIE_HTTPONLY = False  # Le JS doit pouvoir lire le cookie CSRF
# # CSRF_COOKIE_SAMESITE = 'Lax'

# # Option 2 : Exempter les endpoints API du CSRF (moins sécurisé)
# # CSRF_TRUSTED_ORIGINS = ['https://monecole.gn']

# # ── Logging authentication ────────────────────────────────────────────────────
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
