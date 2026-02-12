from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache backend for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Celery settings for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True