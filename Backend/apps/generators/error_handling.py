"""
Centralized error handling decorators and utilities.
Eliminates duplicate error handling patterns across views.
"""

import logging
import traceback
from functools import wraps
from typing import Dict, Any, Optional, Callable, Type
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from .exceptions_unified import (
    BaseGeneratorError,
    GenerationLimitError,
    PromptInjectionError,
    LLMServiceError,
    ServiceUnavailableError,
    RateLimitError,
    TimeoutError,
    ValidationError
)

logger = logging.getLogger(__name__)


# Error code to HTTP status mapping
ERROR_STATUS_MAPPING = {
    # Generator errors
    'GENERATION_LIMIT_EXCEEDED': status.HTTP_429_TOO_MANY_REQUESTS,
    'PROMPT_INJECTION_DETECTED': status.HTTP_400_BAD_REQUEST,
    'CONTENT_VALIDATION_FAILED': status.HTTP_422_UNPROCESSABLE_ENTITY,
    'LLM_SERVICE_ERROR': status.HTTP_503_SERVICE_UNAVAILABLE,
    
    # Service errors
    'SERVICE_UNAVAILABLE': status.HTTP_503_SERVICE_UNAVAILABLE,
    'RESOURCE_EXHAUSTED': status.HTTP_429_TOO_MANY_REQUESTS,
    
    # Auth errors
    'AUTHENTICATION_FAILED': status.HTTP_401_UNAUTHORIZED,
    'AUTHORIZATION_FAILED': status.HTTP_403_FORBIDDEN,
    
    # Validation errors
    'VALIDATION_ERROR': status.HTTP_400_BAD_REQUEST,
    
    # Rate limiting
    'RATE_LIMIT_EXCEEDED': status.HTTP_429_TOO_MANY_REQUESTS,
    
    # Timeout
    'TIMEOUT_ERROR': status.HTTP_408_REQUEST_TIMEOUT,
    
    # Default
    'INTERNAL_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def handle_generator_errors(func: Callable) -> Callable:
    """
    Decorator to handle generator errors consistently across all views.
    Eliminates the need for repetitive try-except blocks.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseGeneratorError as e:
            return _handle_generator_error(e)
        except Exception as e:
            return _handle_unexpected_error(e, func.__name__)
    
    return wrapper


def _handle_generator_error(error: BaseGeneratorError) -> Response:
    """Handle known generator errors with appropriate response."""
    # Get status code from mapping
    status_code = ERROR_STATUS_MAPPING.get(error.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Build response data
    response_data = {
        'error': error.message,
        'error_code': error.error_code,
        'status_code': status_code
    }
    
    # Add details if available
    if error.details:
        response_data['details'] = error.details
    
    # Add retry information for rate limits
    if isinstance(error, (GenerationLimitError, RateLimitError)):
        response_data['retry_after'] = error.details.get('retry_after', 60)
    
    # Log warning for client errors, error for server errors
    if status_code >= 500:
        logger.error(f"Generator error: {error.message}", exc_info=True)
    else:
        logger.warning(f"Client error: {error.message}")
    
    return Response(response_data, status=status_code)


def _handle_unexpected_error(error: Exception, function_name: str) -> Response:
    """Handle unexpected errors safely."""
    # Log full error with traceback
    logger.error(
        f"Unexpected error in {function_name}: {str(error)}",
        exc_info=True,
        extra={
            'function': function_name,
            'error_type': error.__class__.__name__
        }
    )
    
    # Build safe error response
    response_data = {
        'error': 'An unexpected error occurred. Please try again later.',
        'error_code': 'INTERNAL_ERROR',
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    
    # Add debug info if in development
    if settings.DEBUG:
        response_data['debug'] = {
            'error_type': error.__class__.__name__,
            'message': str(error),
            'traceback': traceback.format_exc()
        }
    
    return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ErrorHandler:
    """
    Utility class for handling errors consistently.
    Provides methods for common error scenarios.
    """
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None, level: str = 'error'):
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
        details: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Response:
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details
            headers: Additional response headers
            
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
        
        response = Response(response_data, status=status_code)
        
        if headers:
            for key, value in headers.items():
                response[key] = value
        
        return response
    
    @staticmethod
    def handle_validation_error(serializer_errors: Dict[str, Any]) -> Response:
        """
        Handle DRF serializer validation errors.
        
        Args:
            serializer_errors: Errors from DRF serializer
            
        Returns:
            Response with validation errors
        """
        response_data = {
            'error': 'Validation failed',
            'error_code': 'VALIDATION_ERROR',
            'status_code': status.HTTP_400_BAD_REQUEST,
            'field_errors': serializer_errors
        }
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def handle_service_unavailable(service_name: str, retry_after: int = 60) -> Response:
        """
        Handle service unavailable scenarios.
        
        Args:
            service_name: Name of the unavailable service
            retry_after: Seconds after which client should retry
            
        Returns:
            Response with service unavailable error
        """
        return ErrorHandler.create_error_response(
            message=f"{service_name} is temporarily unavailable",
            error_code='SERVICE_UNAVAILABLE',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={'service': service_name},
            headers={'Retry-After': str(retry_after)}
        )
    
    @staticmethod
    def handle_rate_limit(retry_after: int = 60, limit_type: str = 'requests') -> Response:
        """
        Handle rate limit exceeded scenarios.
        
        Args:
            retry_after: Seconds after which client should retry
            limit_type: Type of limit that was exceeded
            
        Returns:
            Response with rate limit error
        """
        return ErrorHandler.create_error_response(
            message=f"Rate limit exceeded. Too many {limit_type}.",
            error_code='RATE_LIMIT_EXCEEDED',
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={'retry_after': retry_after, 'limit_type': limit_type},
            headers={'Retry-After': str(retry_after)}
        )


# Mixin for views to add error handling capabilities
class ErrorHandlingMixin:
    """
    Mixin for Django REST Framework views to add error handling.
    """
    
    def handle_exception(self, exc):
        """
        Handle exceptions in DRF views.
        """
        # Try to handle as generator error
        if isinstance(exc, BaseGeneratorError):
            return _handle_generator_error(exc)
        
        # Fall back to DRF's default handling
        return super().handle_exception(exc)
    
    def error_response(self, message: str, error_code: str = 'ERROR', **kwargs):
        """
        Create an error response from within a view.
        """
        return ErrorHandler.create_error_response(
            message=message,
            error_code=error_code,
            **kwargs
        )


# Context manager for operation error handling
class OperationHandler:
    """
    Context manager for handling operations with consistent error handling.
    """
    
    def __init__(self, operation_name: str, reraise: bool = False):
        self.operation_name = operation_name
        self.reraise = reraise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            ErrorHandler.log_error(
                exc_val,
                context={'operation': self.operation_name}
            )
            
            if not self.reraise:
                # Suppress the exception
                return True
        
        return False


# Decorator for database operations
def handle_database_errors(func: Callable) -> Callable:
    """
    Decorator to handle database errors consistently.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            return ErrorHandler.create_error_response(
                message=str(e),
                error_code=e.error_code,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}", exc_info=True)
            return ErrorHandler.create_error_response(
                message="Database operation failed",
                error_code="DATABASE_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return wrapper


# Import DatabaseError for the decorator
try:
    from .exceptions_unified import DatabaseError
except ImportError:
    # Define a simple DatabaseError if not available
    class DatabaseError(Exception):
        error_code = "DATABASE_ERROR"
