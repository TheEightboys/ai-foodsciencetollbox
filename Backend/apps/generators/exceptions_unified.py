"""
Unified exception module for the generators app.
Consolidates all exceptions from multiple modules.
"""

from typing import Optional, Dict, Any


class BaseGeneratorError(Exception):
    """Base exception for all generator-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


# Generator-specific exceptions
class GeneratorError(BaseGeneratorError):
    """General generator error."""
    pass


class GenerationLimitError(GeneratorError):
    """Raised when user exceeds generation limits."""
    
    def __init__(self, message: str, limit_type: str = "monthly"):
        super().__init__(
            message=message,
            error_code="GENERATION_LIMIT_EXCEEDED",
            details={"limit_type": limit_type}
        )


class LLMServiceError(GeneratorError):
    """Raised when LLM service fails."""
    
    def __init__(self, message: str, service: str = "openai", retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            error_code="LLM_SERVICE_ERROR",
            details={"service": service, "retry_after": retry_after}
        )


class ContentValidationError(GeneratorError):
    """Raised when generated content fails validation."""
    
    def __init__(self, message: str, validation_errors: Optional[list] = None):
        super().__init__(
            message=message,
            error_code="CONTENT_VALIDATION_FAILED",
            details={"validation_errors": validation_errors or []}
        )


class PromptInjectionError(GeneratorError):
    """Raised when prompt injection is detected."""
    
    def __init__(self, message: str = "Suspicious input detected"):
        super().__init__(
            message=message,
            error_code="PROMPT_INJECTION_DETECTED",
            details={"reason": "Input contains potentially malicious content"}
        )


# Service and infrastructure exceptions
class ServiceError(BaseGeneratorError):
    """Base class for service-related errors."""
    pass


class ServiceUnavailableError(ServiceError):
    """Raised when a service is unavailable."""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE"
        )


class ResourceExhaustedError(ServiceError):
    """Raised when resources are exhausted."""
    
    def __init__(self, message: str = "Resource limit exceeded"):
        super().__init__(
            message=message,
            error_code="RESOURCE_EXHAUSTED"
        )


# Authentication and authorization exceptions
class AuthenticationError(ServiceError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED"
        )


class AuthorizationError(ServiceError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED"
        )


# Configuration and setup exceptions
class ConfigurationError(BaseGeneratorError):
    """Raised when there's a configuration error."""
    
    def __init__(self, message: str, setting: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={"setting": setting} if setting else {}
        )


class DependencyError(BaseGeneratorError):
    """Raised when a required dependency is missing."""
    
    def __init__(self, message: str, dependency: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="DEPENDENCY_ERROR",
            details={"dependency": dependency} if dependency else {}
        )


# Validation exceptions
class ValidationError(BaseGeneratorError):
    """Raised when validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": str(value)} if field else {}
        )


# Rate limiting exceptions
class RateLimitError(BaseGeneratorError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after} if retry_after else {}
        )


# Timeout exceptions
class TimeoutError(BaseGeneratorError):
    """Raised when operation times out."""
    
    def __init__(self, message: str = "Operation timed out", timeout: Optional[float] = None):
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            details={"timeout": timeout} if timeout else {}
        )


# Cache exceptions
class CacheError(BaseGeneratorError):
    """Raised when cache operation fails."""
    
    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR"
        )


# Database exceptions
class DatabaseError(BaseGeneratorError):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR"
        )


# Export all exceptions for easy importing
__all__ = [
    # Base
    'BaseGeneratorError',
    
    # Generator errors
    'GeneratorError',
    'GenerationLimitError',
    'LLMServiceError',
    'ContentValidationError',
    'PromptInjectionError',
    
    # Service errors
    'ServiceError',
    'ServiceUnavailableError',
    'ResourceExhaustedError',
    
    # Auth errors
    'AuthenticationError',
    'AuthorizationError',
    
    # Config errors
    'ConfigurationError',
    'DependencyError',
    
    # Validation errors
    'ValidationError',
    
    # Rate limiting
    'RateLimitError',
    
    # Timeout
    'TimeoutError',
    
    # Cache
    'CacheError',
    
    # Database
    'DatabaseError',
]
