from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

import dj_database_url

# Use DATABASE_URL if available, otherwise fall back to SQLite for development
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Debug toolbar (optional - only if installed)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += [
            'debug_toolbar',
        ]
        MIDDLEWARE += [
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        ]
        INTERNAL_IPS = [
            '127.0.0.1',
        ]
    except ImportError:
        # debug_toolbar not installed, skip it
        pass

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache backend for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'llm_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'llm-cache',
        'TIMEOUT': 3600,
    },
}

# DRF throttle rates
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'generation': '10/minute',
    },
}