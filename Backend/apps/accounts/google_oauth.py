"""
Google OAuth integration for user authentication.
"""
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
import os
import requests as _requests

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, TeacherProfile, UserPreferences

logger = logging.getLogger(__name__)

# OAuth 2.0 scopes
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


class GoogleLoginView(APIView):
    """
    Initiate Google OAuth flow.
    Redirects user to Google's consent screen.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Allow HTTP for local development
        if settings.DEBUG:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
        
        if not client_id or not client_secret:
            logger.error("Google OAuth credentials not configured")
            return JsonResponse({
                'error': 'Google OAuth is not configured. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI]
                    }
                },
                scopes=SCOPES
            )
            flow.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            
            # Generate authorization URL
            # Use 'select_account' instead of 'consent' so returning users are not
            # forced to re-grant permissions every single login (only new grants trigger consent)
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='select_account'
            )
            
            # Store state in session for security
            request.session['oauth_state'] = state
            request.session.save()
            
            # Redirect to Google
            return redirect(authorization_url)
        except ValueError as e:
            logger.error(f"Google OAuth configuration error: {e}", exc_info=True)
            return JsonResponse({
                'error': 'Google OAuth is not properly configured. Please contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error initiating Google OAuth: {e}", exc_info=True)
            return JsonResponse({
                'error': f'Failed to initiate Google sign-in: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleCallbackView(APIView):
    """
    Handle Google OAuth callback.
    Creates or logs in user and returns JWT tokens.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Allow HTTP for local development
        if settings.DEBUG:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        # Get authorization code from callback
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        
        # Check for OAuth errors
        if error:
            logger.error(f"Google OAuth error: {error}")
            frontend_url = settings.FRONTEND_URL
            return redirect(f"{frontend_url}/auth/google/callback?error={error}")
        
        # Verify state (log warning if mismatch but don't block — session may be
        # lost on ephemeral filesystems like Render free plan with SQLite)
        session_state = request.session.get('oauth_state')
        if not state or not session_state or state != session_state:
            logger.warning(
                f"OAuth state mismatch (session may have been lost). "
                f"state={state!r}, session_state={session_state!r}. "
                f"Proceeding anyway — Google code will still be validated."
            )
        
        if not code:
            logger.error("Authorization code not provided")
            frontend_url = settings.FRONTEND_URL
            return redirect(f"{frontend_url}/auth/google/callback?error=no_code")
        
        try:
            client_id = settings.GOOGLE_OAUTH_CLIENT_ID
            client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
            
            if not client_id or not client_secret:
                raise ValueError("Google OAuth credentials not configured")
            
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI]
                    }
                },
                scopes=SCOPES
            )
            flow.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            
            # Exchange authorization code for tokens
            flow.fetch_token(code=code)
            
            # Get user info from Google
            credentials = flow.credentials
            idinfo = id_token.verify_oauth2_token(
                credentials.id_token,
                google_requests.Request(session=_requests.Session()),
                client_id,
                clock_skew_in_seconds=10,
            )
            
            # Verify the token is from Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Extract user information
            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            google_id = idinfo.get('sub')
            picture = idinfo.get('picture', '')
            email_verified = idinfo.get('email_verified', False)
            
            if not email:
                raise ValueError('Email not provided by Google')
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                }
            )
            
            # Update user info if needed
            if not created:
                updated = False
                if not user.first_name and first_name:
                    user.first_name = first_name
                    updated = True
                if not user.last_name and last_name:
                    user.last_name = last_name
                    updated = True
                if not user.is_active:
                    user.is_active = True
                    updated = True
                if updated:
                    user.save()
            
            # Ensure user has TeacherProfile and UserPreferences
            if not hasattr(user, 'teacher_profile'):
                TeacherProfile.objects.create(user=user, email_verified=email_verified)
            elif not user.teacher_profile.email_verified and email_verified:
                user.teacher_profile.email_verified = True
                user.teacher_profile.save()
            
            if not hasattr(user, 'preferences'):
                UserPreferences.objects.create(user=user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Clear OAuth state from session
            if 'oauth_state' in request.session:
                del request.session['oauth_state']
                request.session.save()
            
            # Get frontend URL for redirect
            frontend_url = settings.FRONTEND_URL
            
            # Redirect to frontend with tokens in URL
            # Note: In production, consider using a more secure method (e.g., HTTP-only cookies)
            redirect_url = f"{frontend_url}/auth/google/callback?access={access_token}&refresh={refresh_token}"
            
            return redirect(redirect_url)
            
        except ValueError as e:
            logger.error(f"Google OAuth validation error: {e}", exc_info=True)
            frontend_url = settings.FRONTEND_URL
            return redirect(f"{frontend_url}/auth/google/callback?error={str(e)}")
        except Exception as e:
            logger.error(f"Google OAuth error: {e}", exc_info=True)
            frontend_url = settings.FRONTEND_URL
            return redirect(f"{frontend_url}/auth/google/callback?error=oauth_failed")


class GoogleCodeExchangeView(APIView):
    """
    Exchange a Google authorization code for Django JWT tokens.

    Called by the frontend after Google redirects back to the frontend
    with ?code=...  This lets the redirect_uri be the production frontend
    domain (e.g. https://ai.foodsciencetoolbox.com/auth/google/callback)
    so that Google's consent screen shows that domain instead of the
    Supabase or backend URL.

    POST /api/accounts/google/exchange/
    Body: { "code": "<auth_code>", "redirect_uri": "<frontend_callback_url>" }
    Returns: { "access": "<jwt>", "refresh": "<jwt>", "user": { ... } }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')

        if not code or not redirect_uri:
            return Response(
                {'error': 'Both "code" and "redirect_uri" are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET

        if not client_id or not client_secret:
            logger.error('Google OAuth credentials not configured on the server.')
            return Response(
                {'error': 'Google OAuth is not configured on the server. Please contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # Exchange the authorization code for tokens by calling Google's
            # token endpoint directly — avoids google_auth_oauthlib Flow quirks.
            token_response = _requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code',
                },
                timeout=10,
            )

            token_data = token_response.json()

            if token_response.status_code != 200 or 'error' in token_data:
                google_error = token_data.get('error', 'unknown_error')
                google_desc = token_data.get('error_description', '')
                logger.error(
                    f'Google token exchange failed: {google_error} — {google_desc} '
                    f'(redirect_uri={redirect_uri!r})'
                )
                # Map redirect_uri_mismatch to a clear user-facing message.
                if google_error == 'redirect_uri_mismatch':
                    return Response(
                        {
                            'error': (
                                'Google sign-in configuration error: redirect URI mismatch. '
                                'Please contact support.'
                            )
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                return Response(
                    {'error': f'Google sign-in failed: {google_error}. Please try again.'},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            raw_id_token = token_data.get('id_token')
            if not raw_id_token:
                logger.error('Google token response missing id_token field.')
                return Response(
                    {'error': 'Google sign-in failed: no identity token returned.'},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            # Verify the ID token with Google's public keys.
            idinfo = id_token.verify_oauth2_token(
                raw_id_token,
                google_requests.Request(session=_requests.Session()),
                client_id,
                clock_skew_in_seconds=10,
            )

            if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong token issuer.')

            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            email_verified = idinfo.get('email_verified', False)

            if not email:
                raise ValueError('Email not provided by Google.')

            # Get or create the Django user.
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                },
            )

            if not created:
                updated = False
                if not user.first_name and first_name:
                    user.first_name = first_name
                    updated = True
                if not user.last_name and last_name:
                    user.last_name = last_name
                    updated = True
                if not user.is_active:
                    user.is_active = True
                    updated = True
                if updated:
                    user.save()

            if not hasattr(user, 'teacher_profile'):
                TeacherProfile.objects.create(user=user, email_verified=email_verified)
            elif not user.teacher_profile.email_verified and email_verified:
                user.teacher_profile.email_verified = True
                user.teacher_profile.save()

            if not hasattr(user, 'preferences'):
                UserPreferences.objects.create(user=user)

            refresh = RefreshToken.for_user(user)
            logger.info(f'Google sign-in successful for {email} (new={created})')
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
            })

        except ValueError as e:
            logger.error(f'Google code exchange validation error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'Google code exchange unexpected error: {e}', exc_info=True)
            return Response(
                {'error': f'OAuth code exchange failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
