"""
Django settings for canicross_project project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Configurar hosts permitidos (incluyendo dominios de Cloudflare y el dominio de producción)
allowed_hosts_default = 'localhost,127.0.0.1,192.168.193.200,.trycloudflare.com,*.cloudflare.com,hikers.mappsco.com'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', allowed_hosts_default).split(',')

# Permitir cualquier host en desarrollo
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    # Asegurar que el dominio de producción está en la lista
    if 'hikers.mappsco.com' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('hikers.mappsco.com')

# Importar configuración de logging
from .logging_config import LOGGING

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    
    # Custom apps
    'accounts',
    'events',
    'participants.apps.ParticipantsConfig',
    'registrations',
    'veterinary',
    'kits',
    'checkin',
    'race_management',
    'results',
    'api',
]

MIDDLEWARE = [
    'utils.middleware.CloudflareProxyMiddleware',  # Debe ser el primero para establecer la IP real
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'utils.middleware.MobileCSRFMiddleware',  # Middleware personalizado para CSRF en móviles
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.RequestLoggingMiddleware',
    'utils.middleware.PerformanceMonitoringMiddleware',
    'utils.middleware.SessionTimeoutMiddleware',
]

ROOT_URLCONF = 'canicross_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utils.context_processors.session_timeout',
            ],
        },
    },
]

WSGI_APPLICATION = 'canicross_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Determine which database to use based on environment
if os.getenv('DB_ENGINE') == 'django.db.backends.mysql':
    # MySQL configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'canicross'),
            'USER': os.getenv('DB_USER', 'canicross'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'L8934-!thgurebvHGRTtnbhg*32'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            }
        }
    }
else:
    # SQLite fallback for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es'  # Spanish (Spain)

TIME_ZONE = 'Europe/Madrid'  # Spain time zone

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,https://*.trycloudflare.com,https://hikers.mappsco.com').split(',')
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Asegurar que hikers.mappsco.com está en la lista para producción
    if 'https://hikers.mappsco.com' not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append('https://hikers.mappsco.com')

# CSRF settings
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,https://*.trycloudflare.com,https://*.cloudflare.com,https://hikers.mappsco.com,http://hikers.mappsco.com').split(',')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

# Configuración para proxies y HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Configuración de hosts permitidos adicionales
if DEBUG:
    if 'hikers.mappsco.com' not in ALLOWED_HOSTS and '*' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('hikers.mappsco.com')
    
    # Asegurar que todos los orígenes CSRF necesarios estén presentes
    if 'https://hikers.mappsco.com' not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append('https://hikers.mappsco.com')
    if 'http://hikers.mappsco.com' not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append('http://hikers.mappsco.com')

# Celery settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@canicross.example.com')

# User model
AUTH_USER_MODEL = 'accounts.User'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'participants:profile'
LOGOUT_REDIRECT_URL = 'events:event_list'

# Session settings
SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
SESSION_COOKIE_AGE = SESSION_TIMEOUT_MINUTES * 60  # Default: 30 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Update the session on every request to reset the expiry time
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session expires when browser is closed