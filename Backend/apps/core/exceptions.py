from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for the API.
    Ensures CORS headers are included in all error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response
    if response is not None:
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': response.data.get('detail', 'An error occurred'),
            'data': response.data
        }
        
        # Handle validation errors
        if isinstance(response.data, dict) and 'non_field_errors' in response.data:
            custom_response_data['message'] = response.data['non_field_errors'][0]
        
        response.data = custom_response_data
        
        # Ensure CORS headers are included in error responses
        # This is critical for cross-origin requests
        if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Credentials'] = 'true'
        elif hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
            # Get origin from request if available
            request = context.get('request')
            if request:
                origin = request.META.get('HTTP_ORIGIN')
                if origin and origin in settings.CORS_ALLOWED_ORIGINS:
                    response['Access-Control-Allow-Origin'] = origin
                    response['Access-Control-Allow-Credentials'] = 'true'
        
        # Add other CORS headers
        if hasattr(settings, 'CORS_ALLOWED_HEADERS'):
            response['Access-Control-Allow-Headers'] = ', '.join(settings.CORS_ALLOWED_HEADERS)
        if hasattr(settings, 'CORS_ALLOWED_METHODS'):
            response['Access-Control-Allow-Methods'] = ', '.join(settings.CORS_ALLOWED_METHODS)

    # Log the exception
    logger.error(f"API Exception: {exc}", exc_info=True)

    return response