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

    # Keep-alive: start a background thread that pings this server every 10 minutes
    # Render free plan spins down after 15 min of inactivity; this prevents that.
    def _keep_alive():
        import time
        import urllib.request
        api_base = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('API_BASE_URL', '')
        if not api_base:
            logger.info("No RENDER_EXTERNAL_URL / API_BASE_URL set — keep-alive disabled")
            return
        health_url = f"{api_base.rstrip('/')}/api/health/"
        logger.info(f"Keep-alive thread started — pinging {health_url} every 10 min")
        while True:
            time.sleep(600)  # 10 minutes
            try:
                urllib.request.urlopen(health_url, timeout=10)
            except Exception:
                pass  # Silently ignore; the ping itself triggers the wake

    import threading
    keep_alive_thread = threading.Thread(target=_keep_alive, daemon=True)
    keep_alive_thread.start()

except Exception as e:
    logger.error(f"Failed to load WSGI application: {e}", exc_info=True)
    # Re-raise to prevent silent failures
    raise