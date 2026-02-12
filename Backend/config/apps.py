"""
Django App Configuration for config app
"""
from django.apps import AppConfig


class ConfigConfig(AppConfig):
    """Configuration for the config app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'
    
    def ready(self):
        """Called when Django starts - apps are now loaded"""
        # Setup admin site customization after apps are ready
        from .admin import setup_admin_site
        setup_admin_site()

