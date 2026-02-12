"""
Async LLM client for scalable generation.
Uses Celery for background processing and implements proper error handling.
"""

import time
import logging
from typing import Optional, Dict, Any
from celery import shared_task
from django.core.cache import cache
from django.conf import settings
from ..shared.llm_client import LLMClient
from ..exceptions import LLMServiceError, ContentValidationError

logger = logging.getLogger(__name__)


class AsyncLLMService:
    """
    Async LLM service with caching and rate limiting.
    """
    
    def __init__(self, cache_timeout: int = 3600):
        self.cache_timeout = cache_timeout
        self.rate_limit_cache_key = "llm_rate_limit:{user_id}"
        
    def generate_content_async(self, user_id: int, prompt: str, generator_type: str) -> str:
        """
        Queue content generation for background processing.
        
        Args:
            user_id: User ID for rate limiting
            prompt: The prompt to generate content from
            generator_type: Type of generator (for caching)
            
        Returns:
            Task ID that can be used to check status
        """
        # Check rate limit
        if not self._check_rate_limit(user_id):
            raise LLMServiceError(
                "Rate limit exceeded. Please try again later.",
                retry_after=60
            )
        
        # Check cache first
        cache_key = f"llm_cache:{generator_type}:{hash(prompt)}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for {generator_type} generation")
            return cached_result
        
        # Queue the task
        task = generate_llm_content.delay(
            user_id=user_id,
            prompt=prompt,
            generator_type=generator_type,
            cache_key=cache_key
        )
        
        return task.id
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if within limit, False otherwise
        """
        cache_key = self.rate_limit_cache_key.format(user_id=user_id)
        requests = cache.get(cache_key, 0)
        
        # Get rate limit from settings (default: 10 requests per minute)
        rate_limit = getattr(settings, 'LLM_RATE_LIMIT_PER_MINUTE', 10)
        
        if requests >= rate_limit:
            return False
        
        # Increment counter
        cache.set(cache_key, requests + 1, 60)
        return True
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a generation task.
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Dictionary with task status
        """
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id)
        
        return {
            'task_id': task_id,
            'status': result.state,
            'ready': result.ready(),
            'successful': result.successful() if result.ready() else False,
            'result': result.result if result.ready() else None,
            'error': str(result.info) if result.ready() and not result.successful() else None
        }


@shared_task(bind=True, max_retries=3)
def generate_llm_content(self, user_id: int, prompt: str, generator_type: str, cache_key: str):
    """
    Background task for LLM content generation.
    
    Args:
        user_id: User ID who requested the generation
        prompt: The prompt to generate from
        generator_type: Type of generator
        cache_key: Cache key for storing result
        
    Returns:
        Generated content
    """
    try:
        # Import here to avoid circular imports
        from ..openai_service import OpenAIService
        
        # Create OpenAI service instance
        openai_service = OpenAIService()
        
        # Generate content
        start_time = time.time()
        response = openai_service.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        
        generation_time = time.time() - start_time
        
        if not response.choices or not response.choices[0].message:
            raise LLMServiceError("Empty response from LLM")
        
        content = response.choices[0].message.content
        
        # Validate content
        if not content or len(content.strip()) < 10:
            raise ContentValidationError("Generated content is too short or empty")
        
        # Cache the result
        cache.set(cache_key, content, 3600)
        
        # Log metrics
        logger.info(
            f"Generated {generator_type} content for user {user_id} "
            f"in {generation_time:.2f}s"
        )
        
        return {
            'content': content,
            'generation_time': generation_time,
            'tokens_used': response.usage.total_tokens if response.usage else 0
        }
        
    except Exception as exc:
        logger.error(f"LLM generation failed: {exc}", exc_info=True)
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            logger.info(f"Retrying LLM generation in {countdown} seconds...")
            raise self.retry(countdown=countdown)
        
        # Final attempt failed
        raise LLMServiceError(f"Failed to generate content after {self.max_retries} attempts")


class LLMCacheManager:
    """
    Manages caching for LLM responses.
    """
    
    @staticmethod
    def get_cache_key(generator_type: str, params: Dict[str, Any]) -> str:
        """
        Generate a cache key based on generator type and parameters.
        
        Args:
            generator_type: Type of generator
            params: Generation parameters
            
        Returns:
            Cache key string
        """
        import hashlib
        import json
        
        # Create deterministic string from params
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        
        return f"llm_cache:{generator_type}:{param_hash}"
    
    @staticmethod
    def get_cached_response(cache_key: str) -> Optional[str]:
        """Get cached response if available."""
        return cache.get(cache_key)
    
    @staticmethod
    def cache_response(cache_key: str, response: str, timeout: int = 3600):
        """Cache a response."""
        cache.set(cache_key, response, timeout)
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate all cache entries for a user."""
        # This would require a more sophisticated caching strategy
        # For now, we'll just log it
        logger.info(f"Invalidating cache for user {user_id}")
