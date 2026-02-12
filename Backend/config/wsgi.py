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
except Exception as e:
    logger.error(f"Failed to load WSGI application: {e}", exc_info=True)
    # Re-raise to prevent silent failures
    raise