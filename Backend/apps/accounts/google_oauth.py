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
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
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
        
        # Verify state
        session_state = request.session.get('oauth_state')
        if not state or not session_state or state != session_state:
            logger.error("Invalid OAuth state parameter")
            frontend_url = settings.FRONTEND_URL
            return redirect(f"{frontend_url}/auth/google/callback?error=invalid_state")
        
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
                google_requests.Request(),
                client_id
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

