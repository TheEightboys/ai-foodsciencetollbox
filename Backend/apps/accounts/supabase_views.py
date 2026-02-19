"""
Supabase JWT token exchange endpoint.

Flow:
  1. Frontend signs the user in via Supabase (email/password or Google OAuth).
  2. Frontend POSTs the Supabase access token to this view.
  3. We verify the token by calling the Supabase /auth/v1/user endpoint.
  4. We create or get the matching Django User.
  5. We return a Django JWT access + refresh pair so the rest of the app
     continues to work exactly as before.
"""
import logging
import requests as http_requests

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
User = get_user_model()


class SupabaseTokenExchangeView(APIView):
    """
    POST /api/accounts/supabase-token/
    Body: { "supabase_token": "<supabase-access-token>" }
    Returns: { "access": "...", "refresh": "...", "user": { id, email, first_name, last_name } }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        supabase_token = request.data.get('supabase_token')
        if not supabase_token:
            return Response({'error': 'supabase_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify token by calling Supabase user endpoint
        supabase_url = getattr(settings, 'SUPABASE_URL', '')
        if not supabase_url:
            logger.error('SUPABASE_URL not configured in Django settings')
            return Response({'error': 'Supabase not configured on server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        supabase_url = supabase_url.rstrip('/')
        try:
            resp = http_requests.get(
                f'{supabase_url}/auth/v1/user',
                headers={
                    'Authorization': f'Bearer {supabase_token}',
                    'apikey': getattr(settings, 'SUPABASE_ANON_KEY', ''),
                },
                timeout=10,
            )
        except http_requests.exceptions.RequestException as e:
            logger.error(f'Supabase user endpoint request failed: {e}')
            return Response({'error': 'Cannot reach Supabase. Please try again.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if resp.status_code != 200:
            logger.warning(f'Supabase token verification failed: {resp.status_code} {resp.text}')
            return Response({'error': 'Invalid or expired Supabase token.'}, status=status.HTTP_401_UNAUTHORIZED)

        supabase_user = resp.json()
        email = supabase_user.get('email', '').lower().strip()
        if not email:
            return Response({'error': 'No email address in Supabase user data.'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract name from user_metadata (set during sign-up or provided by Google)
        metadata = supabase_user.get('user_metadata', {})
        first_name = (
            metadata.get('first_name')
            or metadata.get('given_name')
            or metadata.get('full_name', '').split()[0]
            or ''
        )
        last_name = (
            metadata.get('last_name')
            or metadata.get('family_name')
            or (' '.join(metadata.get('full_name', '').split()[1:]) if metadata.get('full_name') else '')
            or ''
        )
        avatar_url = metadata.get('avatar_url') or metadata.get('picture', '')

        # Create or get the Django user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
            }
        )

        if created:
            # New user — fill profile fields and ensure membership exists
            user.set_unusable_password()
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save()
            logger.info(f'Created new Django user via Supabase token: {email}')
        else:
            # Existing user — update name if blank
            changed = False
            if not user.first_name and first_name:
                user.first_name = first_name
                changed = True
            if not user.last_name and last_name:
                user.last_name = last_name
                changed = True
            if changed:
                user.save()

        # Ensure a TeacherProfile exists (signals may handle this but be safe)
        try:
            from apps.accounts.models import TeacherProfile
            TeacherProfile.objects.get_or_create(user=user)
        except Exception:
            pass

        # Generate Django JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
        }, status=status.HTTP_200_OK)
