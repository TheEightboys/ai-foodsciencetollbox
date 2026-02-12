from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FeatureNotificationRequest
import logging

logger = logging.getLogger(__name__)


class FeatureNotificationRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Save a feature notification request"""
        feature_name = request.data.get('feature_name')
        user_email = request.data.get('user_email')

        if not feature_name:
            return Response({
                'error': 'Feature name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create or get existing notification request
            notification, created = FeatureNotificationRequest.objects.get_or_create(
                user=request.user,
                feature_name=feature_name,
                defaults={'user_email': user_email or request.user.email}
            )

            if created:
                logger.info(f"Feature notification request created: {request.user.email} - {feature_name}")
                return Response({
                    'message': f'You will be notified when {feature_name} is available.',
                    'created': True
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': f'You are already on the notification list for {feature_name}.',
                    'created': False
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error creating feature notification request: {e}", exc_info=True)
            return Response({
                'error': 'Failed to save notification request'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


