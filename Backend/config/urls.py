"""
URL configuration for ai_teaching_assistant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseNotFound
from apps.core.views import health_check
from django.http import JsonResponse

def root_view(request):
    """Root endpoint to verify backend is running"""
    from django.conf import settings
    return JsonResponse({
        'status': 'ok',
        'message': 'Food Science Toolbox Teaching Assistant API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health/',
            'admin': '/admin/',
            'api': '/api/',
        },
        'debug': getattr(settings, 'DEBUG', False),
    })

def api_root_view(request):
    """API root endpoint listing all available endpoints"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Food Science Toolbox Teaching Assistant API',
        'version': '1.0.0',
        'endpoints': {
            'accounts': '/api/accounts/',
            'memberships': '/api/memberships/',
            'payments': '/api/payments/',
            'generators': '/api/generators/',
            'admin_dashboard': '/api/admin-dashboard/',
            'legal': '/api/legal/',
            'health': '/api/health/',
        },
        'authentication': {
            'register': '/api/accounts/register/',
            'login': '/api/accounts/login/',
            'logout': '/api/accounts/logout/',
            'token_refresh': '/api/accounts/token/refresh/',
        }
    })

def favicon_view(request):
    """Handle favicon requests to prevent 500 errors"""
    return HttpResponseNotFound()

urlpatterns = [
    path('', root_view, name='root'),
    path('favicon.ico', favicon_view, name='favicon'),
    path('admin/', admin.site.urls),
    # API endpoints - more specific paths first
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/memberships/', include('apps.memberships.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/generators/', include('apps.generators.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/admin-dashboard/', include('apps.admin_dashboard.urls')),
    path('api/legal/', include('apps.legal.urls')),
    path('api/health/', health_check, name='health-check'),
    path('api/health', health_check, name='health-check-no-slash'),  # Without trailing slash
    # API root - use re_path to explicitly match /api without trailing slash
    # This must come before the pattern with trailing slash to match first
    re_path(r'^api$', api_root_view, name='api-root-no-slash'),  # Without trailing slash - must come first
    path('api/', api_root_view, name='api-root'),  # With trailing slash
]

# Conditionally include downloads URLs to handle import errors gracefully
# Downloads app may have dependencies that aren't available, so we handle it gracefully
import logging
logger = logging.getLogger(__name__)

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        # debug_toolbar not installed, skip it
        pass