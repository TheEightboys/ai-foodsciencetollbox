"""
WSGI config for ai_teaching_assistant project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import logging

# Set up logging before Django initialization
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)

# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logger.info("WSGI application loaded successfully")

    # Auto-run migrations on startup (needed for SQLite on ephemeral filesystems like Render free plan)
    # This ensures tables exist even when the Start Command doesn't include migrate
    try:
        from django.core.management import call_command
        from django.conf import settings as django_settings
        db_engine = django_settings.DATABASES.get('default', {}).get('ENGINE', '')
        if 'sqlite3' in db_engine:
            logger.info("SQLite detected — running migrations on startup...")
            call_command('migrate', '--noinput', verbosity=1)
            logger.info("Migrations completed successfully")
    except Exception as mig_err:
        logger.warning(f"Auto-migration failed (non-fatal): {mig_err}")

except Exception as e:
    logger.error(f"Failed to load WSGI application: {e}", exc_info=True)
    # Re-raise to prevent silent failures
    raise