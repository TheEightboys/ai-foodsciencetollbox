# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# Make celery import optional to prevent startup failures
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except (ImportError, Exception) as e:
    # Celery not available or misconfigured - continue without it
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Celery not available: {e}. Continuing without Celery.")
    celery_app = None
    __all__ = ()