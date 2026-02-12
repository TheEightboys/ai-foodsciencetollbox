"""
Enterprise resilience patterns for fault tolerance.
Implements circuit breaker, bulkhead, retry, and timeout patterns.
"""

import time
import logging
from typing import Any, Callable, Optional, Dict, List
from functools import wraps
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import pybreaker

logger = logging.getLogger(__name__)


class CircuitBreakerManager:
    """
    Manages circuit breakers for different services.
    """
    
    _breakers: Dict[str, pybreaker.CircuitBreaker] = {}
    
    @classmethod
    def get_breaker(cls, name: str, **kwargs) -> pybreaker.CircuitBreaker:
        """Get or create a circuit breaker for a service."""
        if name not in cls._breakers:
            default_config = {
                'fail_max': getattr(settings, 'CIRCUIT_BREAKER_FAIL_MAX', 5),
                'reset_timeout': getattr(settings, 'CIRCUIT_BREAKER_RESET_TIMEOUT', 60),
                'exclude': (ConnectionError, TimeoutError),
            }
            default_config.update(kwargs)
            cls._breakers[name] = pybreaker.CircuitBreaker(**default_config)
        return cls._breakers[name]
    
    @classmethod
    def circuit_breaker(cls, service_name: str, **kwargs):
        """Decorator for circuit breaker protection."""
        breaker = cls.get_breaker(service_name, **kwargs)
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return breaker.call(func, *args, **kwargs)
                except pybreaker.CircuitBreakerError:
                    logger.error(f"Circuit breaker open for service: {service_name}")
                    raise ServiceUnavailableError(f"Service {service_name} is currently unavailable")
            return wrapper
        return decorator


class BulkheadManager:
    """
    Implements bulkhead pattern for resource isolation.
    """
    
    def __init__(self):
        self.semaphores: Dict[str, Any] = {}
        self.queues: Dict[str, List] = {}
    
    def get_semaphore(self, name: str, max_concurrent: int = 10):
        """Get a semaphore for resource limiting."""
        if name not in self.semaphores:
            from threading import Semaphore
            self.semaphores[name] = Semaphore(max_concurrent)
        return self.semaphores[name]
    
    def bulkhead(self, name: str, max_concurrent: int = 10, queue_size: int = 100):
        """Decorator for bulkhead pattern."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                semaphore = self.get_semaphore(name, max_concurrent)
                
                # Try to acquire semaphore with timeout
                acquired = semaphore.acquire(timeout=5)
                if not acquired:
                    raise ResourceExhaustedError(f"Service {name} is at capacity")
                
                try:
                    return func(*args, **kwargs)
                finally:
                    semaphore.release()
            return wrapper
        return decorator


class RetryManager:
    """
    Implements retry with exponential backoff and jitter.
    """
    
    @staticmethod
    def retry(
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """Decorator for retry logic."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        # Don't retry on certain exceptions
                        if isinstance(e, (AuthenticationError, AuthorizationError)):
                            raise
                        
                        if attempt < max_attempts - 1:
                            # Calculate delay with exponential backoff
                            delay = min(base_delay * (exponential_base ** attempt), max_delay)
                            
                            # Add jitter to prevent thundering herd
                            if jitter:
                                import random
                                delay *= (0.5 + random.random() * 0.5)
                            
                            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
                            time.sleep(delay)
                
                # All attempts failed
                logger.error(f"All {max_attempts} attempts failed: {last_exception}")
                raise last_exception
            return wrapper
        return decorator


class TimeoutManager:
    """
    Implements timeout patterns for operations.
    """
    
    @staticmethod
    def timeout(seconds: float):
        """Decorator for timeout protection."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Operation timed out after {seconds} seconds")
                
                # Set timeout
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(seconds))
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    # Clean up
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
            
            return wrapper
        return decorator


class ResilientLLMService:
    """
    Enterprise-grade LLM service with all resilience patterns.
    """
    
    def __init__(self):
        self.circuit_breaker = CircuitBreakerManager.get_breaker(
            'llm_service',
            fail_max=5,
            reset_timeout=60
        )
        self.bulkhead = BulkheadManager().get_semaphore(
            'llm_calls',
            max_concurrent=getattr(settings, 'LLM_MAX_CONCURRENT', 20)
        )
    
    @CircuitBreakerManager.circuit_breaker('openai_api')
    @BulkheadManager().bulkhead('openai_calls', max_concurrent=10)
    @RetryManager.retry(max_attempts=3, base_delay=1.0)
    @TimeoutManager.timeout(30)
    def generate_with_resilience(self, prompt: str, **kwargs) -> str:
        """Generate content with full resilience protection."""
        # Actual LLM call here
        from ..openai_service import OpenAIService
        service = OpenAIService()
        
        response = service.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        return response.choices[0].message.content


class HealthChecker:
    """
    Health checking for services with dependency tracking.
    """
    
    def __init__(self):
        self.health_status: Dict[str, Dict] = {}
    
    def check_health(self, service_name: str, check_func: Callable) -> bool:
        """Check health of a service."""
        start_time = time.time()
        
        try:
            result = check_func()
            duration = time.time() - start_time
            
            self.health_status[service_name] = {
                'healthy': True,
                'last_check': datetime.utcnow(),
                'response_time': duration,
                'error': None
            }
            
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            
            self.health_status[service_name] = {
                'healthy': False,
                'last_check': datetime.utcnow(),
                'response_time': duration,
                'error': str(e)
            }
            
            logger.error(f"Health check failed for {service_name}: {e}")
            return False
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        total_services = len(self.health_status)
        healthy_services = sum(1 for s in self.health_status.values() if s['healthy'])
        
        return {
            'overall_healthy': healthy_services == total_services,
            'healthy_services': healthy_services,
            'total_services': total_services,
            'services': self.health_status
        }


class GracefulDegradation:
    """
    Implements graceful degradation when services fail.
    """
    
    def __init__(self):
        self.fallback_strategies: Dict[str, Callable] = {}
    
    def register_fallback(self, service: str, fallback_func: Callable):
        """Register a fallback strategy."""
        self.fallback_strategies[service] = fallback_func
    
    def execute_with_fallback(self, service: str, primary_func: Callable, *args, **kwargs):
        """Execute with fallback on failure."""
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary service {service} failed: {e}, using fallback")
            
            if service in self.fallback_strategies:
                return self.fallback_strategies[service](*args, **kwargs)
            else:
                raise ServiceUnavailableError(f"No fallback available for {service}")


# Custom exceptions
class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable."""
    pass


class ResourceExhaustedError(Exception):
    """Raised when resources are exhausted."""
    pass


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when authorization fails."""
    pass


# Decorator for combining all patterns
def resilient_service(
    service_name: str,
    max_concurrent: int = 10,
    max_attempts: int = 3,
    timeout_seconds: float = 30
):
    """
    Combined decorator for full resilience.
    """
    def decorator(func):
        @wraps(func)
        @CircuitBreakerManager.circuit_breaker(service_name)
        @BulkheadManager().bulkhead(f"{service_name}_calls", max_concurrent=max_concurrent)
        @RetryManager.retry(max_attempts=max_attempts)
        @TimeoutManager.timeout(timeout_seconds)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
