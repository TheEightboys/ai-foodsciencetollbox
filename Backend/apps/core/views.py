from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


def _add_cors_headers(response):
    """Add CORS headers to health check responses."""
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response['Access-Control-Max-Age'] = '86400'
    return response


@csrf_exempt
def health_check(request):
    """
    Health check endpoint — plain Django view (not DRF) so it works with
    any HTTP method and always returns proper CORS headers.
    """
    # Handle OPTIONS preflight and HEAD
    if request.method in ('OPTIONS', 'HEAD'):
        return _add_cors_headers(HttpResponse(status=200))

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

        # Check cache connection (optional)
        cache_status = False
        try:
            cache.set('health_check', 'ok', 30)
            cache_status = cache.get('health_check') == 'ok'
        except Exception as e:
            logger.warning(f"Cache health check failed: {e}")

        response_data = {
            'status': 'healthy' if db_status else 'degraded',
            'database': 'connected' if db_status else 'disconnected',
            'cache': 'connected' if cache_status else 'disconnected',
            'overall': 'ok' if db_status else 'degraded',
        }
        if db_error:
            response_data['database_error'] = db_error[:100]

        return _add_cors_headers(JsonResponse(response_data, status=200))

    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return _add_cors_headers(JsonResponse({
            'status': 'error',
            'error': 'Internal error',
            'overall': 'error',
        }, status=200))