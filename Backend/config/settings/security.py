"""
Security-focused settings updates for production.
"""

from .base import *
import os
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# SECURITY SETTINGS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True

# SSL Settings (only enable if using HTTPS)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)

# CORS Settings - Restrict to specific domains
CORS_ALLOWED_ORIGINS = [
    'https://ai.foodsciencetoolbox.com',
    'https://www.foodsciencetoolbox.com',
    'http://localhost:8080',
    'http://localhost:8000',
]

# Development origins (remove in production)
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        'http://localhost:3000',
        'http://localhost:5173',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
    ])

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# Rate Limiting Settings
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# LLM Security Settings
MAX_GENERATOR_INPUT_LENGTH = 2000
LLM_RATE_LIMIT_PER_MINUTE = 10
USE_ASYNC_GENERATION = True

# OpenAI Settings
OPENAI_API_KEY = config('OPENAI_API_KEY')
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.7
OPENAI_MODEL = 'gpt-4o'

# Cache Settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
        }
    },
    'llm_cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/2'),
        'TIMEOUT': 3600,  # 1 hour
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'generators': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security Headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.openai.com",
}

# Middleware to add security headers
MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'apps.generators.middleware.SecurityHeadersMiddleware',
]

# Database Connection Pooling
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
}

# Celery Configuration for async tasks
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/3')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# API Settings
REST_FRAMEWORK.update({
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'generation': '10/minute'
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'EXCEPTION_HANDLER': 'apps.generators.exceptions.custom_exception_handler',
})

# Monitoring and Observability
ENABLE_METRICS = config('ENABLE_METRICS', default=True, cast=bool)
METRICS_ENABLED = ENABLE_METRICS

# OpenTelemetry Configuration (if enabled)
if ENABLE_METRICS:
    OPENTELEMETRY_ENABLED = True
    JAEGER_AGENT_HOST = config('JAEGER_AGENT_HOST', default='localhost')
    JAEGER_AGENT_PORT = config('JAEGER_AGENT_PORT', default=6831, cast=int)
