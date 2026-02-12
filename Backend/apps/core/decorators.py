"""
CORS decorator to ensure CORS headers are added to views.
This is a fallback in case middleware doesn't work.
"""
from functools import wraps
from django.conf import settings
from django.http import HttpResponse


def cors_headers(view_func):
    """
    Decorator to add CORS headers to a view response.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Handle OPTIONS preflight
        if request.method == 'OPTIONS':
            response = HttpResponse(status=200)
            _add_cors_headers(response, request)
            return response
        
        # Call the view
        response = view_func(request, *args, **kwargs)
        
        # Add CORS headers to response
        _add_cors_headers(response, request)
        
        return response
    
    return wrapped_view


def _add_cors_headers(response, request):
    """
    Add CORS headers to the response.
    """
    origin = request.META.get('HTTP_ORIGIN', '')
    allow_credentials = getattr(settings, 'CORS_ALLOW_CREDENTIALS', False)
    allow_all_origins = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
    
    # Determine allowed origin
    if allow_all_origins:
        if origin:
            response['Access-Control-Allow-Origin'] = origin
        elif not allow_credentials:
            response['Access-Control-Allow-Origin'] = '*'
    elif origin:
        response['Access-Control-Allow-Origin'] = origin
    
    if allow_credentials:
        response['Access-Control-Allow-Credentials'] = 'true'
    
    if hasattr(settings, 'CORS_ALLOWED_METHODS') and settings.CORS_ALLOWED_METHODS:
        response['Access-Control-Allow-Methods'] = ', '.join(settings.CORS_ALLOWED_METHODS)
    
    if hasattr(settings, 'CORS_ALLOWED_HEADERS') and settings.CORS_ALLOWED_HEADERS:
        response['Access-Control-Allow-Headers'] = ', '.join(settings.CORS_ALLOWED_HEADERS)
    
    if hasattr(settings, 'CORS_PREFLIGHT_MAX_AGE') and settings.CORS_PREFLIGHT_MAX_AGE:
        response['Access-Control-Max-Age'] = str(settings.CORS_PREFLIGHT_MAX_AGE)
