"""
Security middleware for adding security headers and enforcing policies.
"""

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to the response.
        """
        # Get security headers from settings
        security_headers = getattr(settings, 'SECURITY_HEADERS', {})
        
        # Add each security header
        for header, value in security_headers.items():
            response[header] = value
        
        # Remove server header
        response.pop('Server', None)
        
        # Add custom headers for API
        if request.path.startswith('/api/'):
            response['X-API-Version'] = '1.0'
            response['X-Powered-By'] = 'TeachAI Assistant'
        
        return response


class InputValidationMiddleware(MiddlewareMixin):
    """
    Middleware to validate and sanitize inputs at the request level.
    """
    
    def process_request(self, request):
        """
        Validate request inputs before processing.
        """
        # Skip validation for safe methods and static files
        if request.method in ['GET', 'HEAD', 'OPTIONS'] or request.path.startswith('/static/'):
            return None
        
        # Validate Content-Type for API requests
        if request.path.startswith('/api/'):
            content_type = request.content_type or ''
            if not content_type.startswith('application/json'):
                logger.warning(f"Invalid Content-Type for API request: {content_type}")
                return HttpResponse(
                    '{"error": "Content-Type must be application/json"}',
                    status=415,
                    content_type='application/json'
                )
        
        return None


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to enforce rate limiting at the edge.
    """
    
    def process_request(self, request):
        """
        Check rate limits before processing the request.
        """
        # Only apply to generation endpoints
        if not request.path.startswith('/api/generators/') or 'generate' not in request.path:
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Check rate limit (simplified - would use Redis in production)
        from django.core.cache import cache
        cache_key = f"rate_limit:{ip}"
        
        # Get current count
        count = cache.get(cache_key, 0)
        limit = getattr(settings, 'RATE_LIMIT_PER_IP', 100)
        
        if count >= limit:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return HttpResponse(
                '{"error": "Rate limit exceeded"}',
                status=429,
                content_type='application/json'
            )
        
        # Increment counter
        cache.set(cache_key, count + 1, 3600)  # 1 hour
        
        return None
