from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# Allow DEBUG to be set via environment variable for troubleshooting
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS - allow all hosts if not specified (for Coolify/reverse proxy)
# Django doesn't support ['*'], so we use an empty list to disable the check
# The reverse proxy (Coolify/Nginx) should handle host validation
ALLOWED_HOSTS_STR = config('ALLOWED_HOSTS', default='*')
if ALLOWED_HOSTS_STR == '*' or ALLOWED_HOSTS_STR == '':
    # ['*'] disables ALLOWED_HOSTS check (safe behind reverse proxy)
    # In production, the reverse proxy validates the Host header
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [s.strip() for s in ALLOWED_HOSTS_STR.split(',') if s.strip()]

# CORS settings for production - allow all origins by default for dynamic subdomains
# This is safe when behind a reverse proxy that validates requests
# Force CORS to allow all origins - this is critical for preflight requests
CORS_ALLOW_ALL_ORIGINS = True  # Force True, don't allow override for now
CORS_ORIGIN_ALLOW_ALL = True  # Alternative setting name (for compatibility)
CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400  # Cache preflight requests for 24 hours
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
    'pragma',
]
CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'HEAD',
]
CORS_EXPOSE_HEADERS = [
    'content-type',
    'x-requested-with',
    'authorization',
    'content-disposition',
    'content-length',
]

# Ensure CORS headers are always sent, even on error responses
CORS_ALLOW_HEADERS = CORS_ALLOWED_HEADERS  # Alias for compatibility

# If specific *production* origins are provided, use them instead.
# Safety: if the env var only contains localhost URLs, keep CORS_ALLOW_ALL_ORIGINS=True
# so the production frontend is not accidentally blocked.
CORS_ALLOWED_ORIGINS_STR = config('CORS_ALLOWED_ORIGINS', default='')
if CORS_ALLOWED_ORIGINS_STR and CORS_ALLOWED_ORIGINS_STR != '*':
    _origins = [s.strip() for s in CORS_ALLOWED_ORIGINS_STR.split(',') if s.strip()]
    _has_production = any(o for o in _origins if 'localhost' not in o and '127.0.0.1' not in o)
    if _has_production:
        CORS_ALLOW_ALL_ORIGINS = False
        CORS_ALLOWED_ORIGINS = _origins
    # else: keep CORS_ALLOW_ALL_ORIGINS = True (set above)

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
import dj_database_url

# Use DATABASE_URL if available, otherwise fall back to individual settings
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=60,   # reduced from 600 — frees DB connections between requests on free plan
            conn_health_checks=True,
        )
    }
    # SSL mode — Supabase and most cloud Postgres providers require SSL
    if 'OPTIONS' not in DATABASES['default']:
        DATABASES['default']['OPTIONS'] = {}
    DB_SSL = config('DB_SSL_REQUIRE', default='true', cast=bool)  # Default True for Supabase
    DATABASES['default']['OPTIONS']['sslmode'] = 'require' if DB_SSL else 'prefer'
else:
    # No DATABASE_URL: use SQLite as lightweight fallback
    import os as _os
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': _os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
# Disable SSL redirect - let reverse proxy (Coolify/Nginx) handle SSL
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
# Only set secure cookies if we're behind HTTPS (reverse proxy should set this)
# For Coolify/reverse proxy setups, these should be False to allow HTTP internally
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# Trust proxy headers from Render / reverse proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# API_BASE_URL - used to build absolute download URLs in API responses
# Set this env var in Render/Coolify to match the backend's public URL
API_BASE_URL = config('API_BASE_URL', default='https://ai-foodsciencetollbox.onrender.com')

# ── Production overrides for OAuth / frontend URLs ────────────────────────────
# These override the localhost defaults from base.py
# Safety: if FRONTEND_URL contains localhost, force production URL
_frontend = config('FRONTEND_URL', default='https://ai.foodsciencetoolbox.com')
if 'localhost' in _frontend or '127.0.0.1' in _frontend:
    FRONTEND_URL = 'https://ai.foodsciencetoolbox.com'
else:
    FRONTEND_URL = _frontend

_redirect = config(
    'GOOGLE_OAUTH_REDIRECT_URI',
    default=f'{API_BASE_URL}/api/accounts/google/callback/'
)
if 'localhost' in _redirect or '127.0.0.1' in _redirect:
    GOOGLE_OAUTH_REDIRECT_URI = f'{API_BASE_URL}/api/accounts/google/callback/'
else:
    GOOGLE_OAUTH_REDIRECT_URI = _redirect

# Session cookie settings for cross-origin OAuth flow
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

# CSRF Trusted Origins - allow API domain and frontend domain
CSRF_TRUSTED_ORIGINS_STR = config('CSRF_TRUSTED_ORIGINS', default='')
if CSRF_TRUSTED_ORIGINS_STR:
    CSRF_TRUSTED_ORIGINS = [s.strip() for s in CSRF_TRUSTED_ORIGINS_STR.split(',') if s.strip()]
else:
    # Default to API domain and common frontend domains
    CSRF_TRUSTED_ORIGINS = [
        'https://api.foodsciencetoolbox.com',
        'https://ai.foodsciencetoolbox.com',
        'https://ai-foodsciencetollbox.onrender.com',
        'http://api.foodsciencetoolbox.com',
        'http://ai.foodsciencetoolbox.com',
    ]

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TIMEOUT = 10  # Timeout in seconds to prevent hanging SMTP connections

# Cache backend for production - fallback to local memory if Redis unavailable
REDIS_URL = config('REDIS_URL', default=None)
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        },
        'llm_cache': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'TIMEOUT': 3600,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Fallback to local memory cache if Redis not configured
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        },
        'llm_cache': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'llm-cache',
            'TIMEOUT': 3600,
        }
    }

# Celery: disable when no Redis available (Render free plan)
if not REDIS_URL:
    CELERY_TASK_ALWAYS_EAGER = True      # Execute tasks synchronously (no broker needed)
    CELERY_TASK_EAGER_PROPAGATES = True   # Propagate exceptions in eager mode
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'