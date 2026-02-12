from django.urls import path
from .views import FeatureNotificationRequestView

app_name = 'notifications'

urlpatterns = [
    path('feature-request/', FeatureNotificationRequestView.as_view(), name='feature-request'),
]


