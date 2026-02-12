"""
Base generator class to eliminate code duplication.
Provides common functionality for all generators.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from rest_framework import serializers
from ..shared.llm_client import LLMClient
from ..exceptions_unified import GeneratorError, LLMServiceError, ContentValidationError
from ..models import GeneratedContent
from ..utils.input_sanitizer import InputSanitizer

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    Abstract base class for all content generators.
    Implements common patterns and enforces consistent behavior.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or OpenAILLMClient()
        
    @abstractmethod
    def get_content_type(self) -> str:
        """Return the content type for this generator."""
        pass
    
    @abstractmethod
    def build_prompt(self, validated_data: Dict[str, Any]) -> str:
        """Build the prompt for LLM generation."""
        pass
    
    @abstractmethod
    def validate_generated_content(self, content: str, validated_data: Dict[str, Any]) -> tuple[bool, list]:
        """
        Validate generated content.
        
        Args:
            content: Generated content from LLM
            validated_data: Original input data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass
    
    @abstractmethod
    def get_serializer_class(self) -> Type[serializers.Serializer]:
        """Return the serializer class for this generator."""
        pass
    
    def generate(self, user, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main generation method with consistent error handling.
        
        Args:
            user: User instance
            request_data: Validated request data
            
        Returns:
            Dictionary with generation result
            
        Raises:
            GeneratorError: For generation-related errors
            LLMServiceError: For LLM service errors
        """
        start_time = time.time()
        
        try:
            # Validate and sanitize input
            validated_data = self._validate_and_sanitize(request_data)
            
            # Generate content synchronously
            return self._generate_sync(user, validated_data)
                
        except Exception as e:
            logger.error(f"Generation failed for {self.get_content_type()}: {e}", exc_info=True)
            raise GeneratorError(f"Failed to generate content: {str(e)}")
    
    def _validate_and_sanitize(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize input data."""
        serializer = self.get_serializer_class()(data=request_data)
        if not serializer.is_valid():
            raise GeneratorError(f"Invalid input: {serializer.errors}")
        
        # Sanitize all string fields
        validated_data = serializer.validated_data
        sanitized_data = InputSanitizer.validate_json_input(validated_data)
        
        return sanitized_data
    
    def _generate_sync(self, user, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content synchronously."""
        if not self.llm_client:
            raise GeneratorError("LLM client not configured for synchronous generation")
        
        # Build prompt
        prompt = self.build_prompt(validated_data)
        
        # Generate content
        generation_start = time.time()
        content = self.llm_client.generate_text(prompt)
        generation_time = time.time() - generation_start
        
        # Validate content
        is_valid, errors = self.validate_generated_content(content, validated_data)
        if not is_valid:
            raise ContentValidationError(
                "Generated content failed validation",
                validation_errors=errors
            )
        
        # Save to database
        self._save_generated_content(user, validated_data, content, generation_time)
        
        return self._build_response(content, generation_time, 0)
    
    def _save_generated_content(self, user, validated_data: Dict[str, Any], content: str, generation_time: float):
        """Save generated content to database."""
        with transaction.atomic():
            GeneratedContent.objects.create(
                user=user,
                content_type=self.get_content_type(),
                title=self._generate_title(validated_data),
                content=content,
                input_parameters=validated_data,
                generation_time=generation_time,
                tokens_used=0  # Would be calculated based on actual usage
            )
    
    def _generate_title(self, validated_data: Dict[str, Any]) -> str:
        """Generate a title for the content."""
        # Default implementation - can be overridden
        topic = validated_data.get('topic', 'Generated Content')
        return f"{self.get_content_type().title()}: {topic}"
    
    def _build_response(self, content: str, generation_time: float, tokens_used: int, from_cache: bool = False) -> Dict[str, Any]:
        """Build a consistent response format."""
        response = {
            'content': content,
            'generation_time': generation_time,
            'tokens_used': tokens_used,
            'from_cache': from_cache
        }
        
        # Add metadata if available
        if hasattr(self, '_metadata'):
            response['metadata'] = self._metadata
            
        return response


class GeneratorFactory:
    """
    Factory for creating generator instances.
    Implements dependency injection for better testability.
    """
    
    _generators = {}
    
    @classmethod
    def register(cls, content_type: str, generator_class: Type[BaseGenerator]):
        """Register a generator class."""
        cls._generators[content_type] = generator_class
    
    @classmethod
    def create(cls, content_type: str, **kwargs) -> BaseGenerator:
        """Create a generator instance."""
        if content_type not in cls._generators:
            raise GeneratorError(f"Unknown generator type: {content_type}")
        
        generator_class = cls._generators[content_type]
        return generator_class(**kwargs)
    
    @classmethod
    def get_available_generators(cls) -> list:
        """Get list of available generator types."""
        return list(cls._generators.keys())


# Mixin for common view functionality
class GeneratorViewMixin:
    """
    Mixin providing common functionality for generator views.
    """
    
    def get_generator(self, content_type: str) -> BaseGenerator:
        """Get generator instance for the given content type."""
        return GeneratorFactory.create(
            content_type,
            use_async=getattr(settings, 'USE_ASYNC_GENERATION', True)
        )
    
    def handle_generation_request(self, request, content_type: str):
        """Handle a generation request with consistent error handling."""
        try:
            generator = self.get_generator(content_type)
            result = generator.generate(request.user, request.data)
            
            if result.get('status') == 'processing':
                # Async generation
                return Response(result, status=status.HTTP_202_ACCEPTED)
            else:
                # Sync generation
                return Response(result, status=status.HTTP_201_CREATED)
                
        except GeneratorError as e:
            return self._handle_generator_error(e)
        except Exception as e:
            logger.error(f"Unexpected error in generation: {e}", exc_info=True)
            return Response({
                'error': 'An unexpected error occurred',
                'error_code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _handle_generator_error(self, error: GeneratorError):
        """Handle generator errors with consistent response format."""
        status_code = self._get_status_code_for_error(error)
        
        response_data = {
            'error': error.message,
            'error_code': error.error_code or 'GENERATOR_ERROR'
        }
        
        if error.details:
            response_data['details'] = error.details
            
        return Response(response_data, status=status_code)
    
    def _get_status_code_for_error(self, error: GeneratorError) -> int:
        """Map error types to HTTP status codes."""
        from ..exceptions import GenerationLimitError, PromptInjectionError
        
        if isinstance(error, GenerationLimitError):
            return status.HTTP_429_TOO_MANY_REQUESTS
        elif isinstance(error, PromptInjectionError):
            return status.HTTP_400_BAD_REQUEST
        elif isinstance(error, LLMServiceError):
            return status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
