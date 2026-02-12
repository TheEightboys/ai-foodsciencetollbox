"""
Custom exception handler for consistent error responses.
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied
from .exceptions import GeneratorError, GenerationLimitError, LLMServiceError, ContentValidationError, PromptInjectionError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error responses.
    
    Args:
        exc: The exception that was raised
        context: The context in which the exception was raised
        
    Returns:
        Response with standardized error format
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    # If DRF handled it, customize the response
    if response is not None:
        # Standardize the error format
        custom_response_data = {
            'error': response.data.get('detail', 'An error occurred'),
            'error_code': getattr(exc, 'code', 'VALIDATION_ERROR'),
            'status_code': response.status_code
        }
        
        # Add field-specific errors for validation errors
        if hasattr(response.data, 'items'):
            field_errors = {}
            for field, errors in response.data.items():
                if field != 'detail' and isinstance(errors, list):
                    field_errors[field] = errors
            
            if field_errors:
                custom_response_data['field_errors'] = field_errors
        
        response.data = custom_response_data
        return response
    
    # Handle our custom exceptions
    if isinstance(exc, GeneratorError):
        return handle_generator_error(exc, context)
    
    # Handle Django built-in exceptions
    if isinstance(exc, Http404):
        return Response({
            'error': 'The requested resource was not found.',
            'error_code': 'NOT_FOUND',
            'status_code': status.HTTP_404_NOT_FOUND
        }, status=status.HTTP_404_NOT_FOUND)
    
    if isinstance(exc, PermissionDenied):
        return Response({
            'error': 'You do not have permission to perform this action.',
            'error_code': 'PERMISSION_DENIED',
            'status_code': status.HTTP_403_FORBIDDEN
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Handle unexpected errors
    logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={'context': context})
    
    return Response({
        'error': 'An unexpected error occurred. Please try again later.',
        'error_code': 'INTERNAL_ERROR',
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_generator_error(exc: GeneratorError, context):
    """
    Handle generator-specific errors.
    
    Args:
        exc: GeneratorError instance
        context: Request context
        
    Returns:
        Response with appropriate status code and error details
    """
    # Map exception types to HTTP status codes
    status_mapping = {
        GenerationLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
        PromptInjectionError: status.HTTP_400_BAD_REQUEST,
        LLMServiceError: status.HTTP_503_SERVICE_UNAVAILABLE,
        ContentValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    
    # Get status code
    status_code = status_mapping.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Build response
    response_data = {
        'error': exc.message,
        'error_code': exc.error_code or 'GENERATOR_ERROR',
        'status_code': status_code
    }
    
    # Add additional details if available
    if exc.details:
        response_data['details'] = exc.details
    
    # Add retry information for rate limit errors
    if isinstance(exc, GenerationLimitError):
        response_data['retry_after'] = 60  # seconds
    
    # Log the error
    logger.warning(
        f"Generator error: {exc.message}",
        extra={
            'error_code': exc.error_code,
            'details': exc.details,
            'context': context
        }
    )
    
    return Response(response_data, status=status_code)


class ErrorHandler:
    """
    Utility class for handling errors consistently across the application.
    """
    
    @staticmethod
    def log_error(error: Exception, context: dict = None, level: str = 'error'):
        """
        Log an error with context.
        
        Args:
            error: The exception to log
            context: Additional context information
            level: Log level (error, warning, info)
        """
        log_method = getattr(logger, level)
        log_method(
            f"{error.__class__.__name__}: {str(error)}",
            extra={
                'error_type': error.__class__.__name__,
                'error_message': str(error),
                'context': context or {}
            },
            exc_info=True
        )
    
    @staticmethod
    def create_error_response(
        message: str,
        error_code: str = 'ERROR',
        status_code: int = 500,
        details: dict = None
    ) -> Response:
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            error_code: Error code for client handling
            status_code: HTTP status code
            details: Additional error details
            
        Returns:
            Response object
        """
        response_data = {
            'error': message,
            'error_code': error_code,
            'status_code': status_code
        }
        
        if details:
            response_data['details'] = details
        
        return Response(response_data, status=status_code)
