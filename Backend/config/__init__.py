# Celery import intentionally disabled for production (Render free tier).
# Celery + redis + django-redis consume ~80 MB of startup RAM without providing
# any value when CELERY_TASK_ALWAYS_EAGER=True and no real broker is present.
# If you re-enable a real Celery broker, restore this import.
__all__ = ()
    logger.warning(f"Celery not available: {e}. Continuing without Celery.")
    celery_app = None
    __all__ = ()