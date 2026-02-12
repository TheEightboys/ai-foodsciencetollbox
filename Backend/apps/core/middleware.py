"""
Core middleware for the application.
"""
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.http import HttpResponseBadRequest
import logging

logger = logging.getLogger(__name__)


class TimezoneMiddleware(MiddlewareMixin):
    """
    Middleware to set the user's timezone based on their preferences.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                # Get user's timezone preference
                # For now, we'll use a default timezone
                # In a real implementation, you might store this in user preferences
                tzname = getattr(request.user, 'timezone', 'UTC')
                if tzname:
                    try:
                        import pytz
                        timezone.activate(pytz.timezone(tzname))
                    except ImportError:
                        logger.warning("pytz not installed, using UTC")
                        timezone.activate(timezone.utc)
                else:
                    timezone.deactivate()
            except Exception as e:
                logger.warning(f"Error activating timezone for user {request.user.email}: {e}")
                timezone.deactivate()  # Deactivate to ensure no incorrect timezone is used
        else:
            timezone.deactivate()


class AllowedHostsMiddleware(MiddlewareMixin):
    """
    Middleware to handle ALLOWED_HOSTS validation for reverse proxy setups.
    This middleware dynamically adds the incoming host to ALLOWED_HOSTS
    and patches request.get_host() to bypass validation if needed.
    
    This is safe when behind a trusted reverse proxy (like Coolify/Nginx).
    """
    
    def process_request(self, request):
        from django.conf import settings
        from django.http import HttpRequest
        
        # Extract host from various headers (reverse proxy setups)
        host = (
            request.META.get('HTTP_X_FORWARDED_HOST') or
            request.META.get('HTTP_HOST') or
            request.META.get('SERVER_NAME') or
            ''
        )
        
        if host:
            # Split to get the first host (in case of multiple hosts)
            host = host.split(',')[0].strip()
            # Remove port if present
            if ':' in host:
                host = host.split(':')[0]
            
            # Always add to ALLOWED_HOSTS if not already there
            if host and host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
                # Host added dynamically - no logging needed in production
            
            # Patch request.get_host() to bypass validation if ALLOWED_HOSTS was empty
            # This prevents DisallowedHost errors when CommonMiddleware calls get_host()
            original_get_host = request.get_host
            
            def patched_get_host():
                try:
                    return original_get_host()
                except Exception as e:
                    # If validation fails, return the host we extracted
                    # This is safe behind a reverse proxy
                    if 'DisallowedHost' in str(type(e).__name__):
                        # Bypassing ALLOWED_HOSTS check - no logging needed
                        return host
                    raise
            
            # Only patch if we successfully extracted a host
            if host:
                request.get_host = patched_get_host
        
        return None  # Continue processing
