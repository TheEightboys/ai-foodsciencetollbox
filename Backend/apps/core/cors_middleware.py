"""
Custom CORS middleware to ensure OPTIONS preflight requests are handled correctly.
This ensures CORS headers are always present, even when django-cors-headers fails.
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


class CustomCorsMiddleware(MiddlewareMixin):
    """
    Custom CORS middleware that explicitly handles OPTIONS requests
    and ensures CORS headers are always present.
    This MUST be the first middleware to handle preflight requests.
    """
    
    def process_request(self, request):
        """
        Handle OPTIONS preflight requests explicitly.
        This intercepts OPTIONS requests before they reach views.
        """
        if request.method == 'OPTIONS':
            origin = request.META.get('HTTP_ORIGIN', '')
            response = HttpResponse(status=200)
            self._add_cors_headers(response, request, origin)
            # Ensure response is returned immediately for OPTIONS
            return response
        return None
    
    def process_response(self, request, response):
        """
        Add CORS headers to all responses.
        """
        origin = request.META.get('HTTP_ORIGIN', '')
        self._add_cors_headers(response, request, origin)
        return response
    
    def _add_cors_headers(self, response, request, origin):
        """
        Add CORS headers to the response.
        """
        # When CORS_ALLOW_CREDENTIALS is True, we MUST use the specific origin, not '*'
        allow_credentials = getattr(settings, 'CORS_ALLOW_CREDENTIALS', False)
        allow_all_origins = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        
        # Determine the origin to allow
        allowed_origin = None
        
        if allow_all_origins:
            # If allowing all origins, always use the requesting origin if present
            # This is required when credentials are enabled (can't use '*')
            if origin:
                allowed_origin = origin
            else:
                # If no origin header, allow all (only safe when credentials disabled)
                if not allow_credentials:
                    allowed_origin = '*'
                # If credentials enabled but no origin, we can't set '*' so skip
        elif hasattr(settings, 'CORS_ALLOWED_ORIGINS') and settings.CORS_ALLOWED_ORIGINS:
            # Check if origin is in allowed list
            if origin in settings.CORS_ALLOWED_ORIGINS:
                allowed_origin = origin
            elif origin:
                # For dynamic subdomains, allow the origin
                allowed_origin = origin
        elif origin:
            # If no specific config but we have an origin, allow it
            allowed_origin = origin
        
        # ALWAYS set the Access-Control-Allow-Origin header
        # This is critical for CORS to work - browsers will reject if missing
        if allowed_origin:
            response['Access-Control-Allow-Origin'] = allowed_origin
        elif allow_all_origins:
            # If allowing all origins but no origin header, use wildcard (only if no credentials)
            if not allow_credentials:
                response['Access-Control-Allow-Origin'] = '*'
            elif origin:
                # If we have an origin, use it
                response['Access-Control-Allow-Origin'] = origin
        elif origin:
            # Last resort: use the requesting origin
            response['Access-Control-Allow-Origin'] = origin
        
        # Add credentials header if enabled
        if allow_credentials:
            response['Access-Control-Allow-Credentials'] = 'true'
        
        # Add allowed methods
        if hasattr(settings, 'CORS_ALLOWED_METHODS') and settings.CORS_ALLOWED_METHODS:
            response['Access-Control-Allow-Methods'] = ', '.join(settings.CORS_ALLOWED_METHODS)
        else:
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
        
        # Add allowed headers
        if hasattr(settings, 'CORS_ALLOWED_HEADERS') and settings.CORS_ALLOWED_HEADERS:
            response['Access-Control-Allow-Headers'] = ', '.join(settings.CORS_ALLOWED_HEADERS)
        else:
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken, Accept, Origin, X-Requested-With'
        
        # Add preflight max age
        if hasattr(settings, 'CORS_PREFLIGHT_MAX_AGE') and settings.CORS_PREFLIGHT_MAX_AGE:
            response['Access-Control-Max-Age'] = str(settings.CORS_PREFLIGHT_MAX_AGE)
        else:
            response['Access-Control-Max-Age'] = '86400'
        
        # Add exposed headers
        if hasattr(settings, 'CORS_EXPOSE_HEADERS') and settings.CORS_EXPOSE_HEADERS:
            response['Access-Control-Expose-Headers'] = ', '.join(settings.CORS_EXPOSE_HEADERS)

