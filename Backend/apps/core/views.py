from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.conf import settings


@api_view(['GET', 'OPTIONS'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint to verify that the application is running correctly.
    Always returns 200 OK to allow reverse proxy health checks to pass.
    Supports OPTIONS for CORS preflight.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        from django.http import HttpResponse
        response = HttpResponse(status=200)
        return response
    
    try:
        # Check database connection
        db_status = False
        db_error = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = True
        except Exception as e:
            db_error = str(e)
            logger.warning(f"Database health check failed: {db_error}")
            
        # Check cache connection (optional - don't fail if cache unavailable)
        cache_status = False
        cache_error = None
        try:
            cache.set('health_check', 'ok', 30)
            cache_status = cache.get('health_check') == 'ok'
        except Exception as e:
            cache_error = str(e)
            logger.warning(f"Cache health check failed: {cache_error}")
            # Cache is optional, so we continue
        
        # Always return 200 OK for health checks (even if DB is down)
        # This allows the reverse proxy to know the app is running
        # The status field indicates actual health
        response_data = {
            'status': 'healthy' if db_status else 'degraded',
            'database': 'connected' if db_status else 'disconnected',
            'cache': 'connected' if cache_status else 'disconnected',
            'overall': 'ok' if db_status else 'degraded'
        }
        
        # Add error details if any (but don't expose sensitive info)
        if db_error:
            # Only show first 100 chars to avoid exposing full connection strings
            response_data['database_error'] = db_error[:100] if len(db_error) <= 100 else db_error[:100] + '...'
        if cache_error:
            response_data['cache_error'] = cache_error[:100] if len(cache_error) <= 100 else cache_error[:100] + '...'
        
        # Always return 200 OK - let the status field indicate health
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        # Even on exception, return 200 OK so reverse proxy doesn't think app is down
        return Response({
            'status': 'error',
            'error': 'Internal error',
            'overall': 'error'
        }, status=status.HTTP_200_OK)