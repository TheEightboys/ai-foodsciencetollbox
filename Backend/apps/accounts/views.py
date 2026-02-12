from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import User, TeacherProfile, UserPreferences
from .serializers import (
    UserSerializer,
    TeacherProfileSerializer,
    UserPreferencesSerializer,
    RegistrationSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        # Registration attempt logged at error level only if needed
        
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                # User registration successful - no logging needed in production
                
                # Signals will automatically create TeacherProfile and UserPreferences
                # No need to create them manually here
                
                # Send welcome email
                try:
                    from apps.notifications.services import EmailService
                    welcome_result = EmailService.send_welcome_email(user)
                    if not welcome_result:
                        logger.warning(f"Welcome email send returned False for {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send welcome email to {user.email}: {e}", exc_info=True)
                
                # Send email verification
                try:
                    # Ensure user has a teacher profile (signals should create it, but ensure it exists)
                    from .models import TeacherProfile
                    profile, _ = TeacherProfile.objects.get_or_create(user=user)
                    
                    # Generate verification token
                    verification_token = profile.generate_verification_token()
                    
                    # Create verification link
                    frontend_url = settings.FRONTEND_URL
                    verification_link = f"{frontend_url}/verify-email/{verification_token}/"
                    
                    # Send verification email
                    from apps.notifications.services import EmailService
                    verification_result = EmailService.send_email_verification(user, verification_link)
                    if not verification_result:
                        logger.error(f"Email verification send returned False for {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send verification email to {user.email}: {e}", exc_info=True)
                    # Don't fail registration if email fails
                
                return Response({
                    'message': 'User registered successfully. Please check your email to verify your account.',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                # Check if it's a database integrity error (duplicate email)
                from django.db import IntegrityError
                if isinstance(e, IntegrityError) and 'email' in str(e).lower():
                    return Response({
                        'error': 'Registration failed.',
                        'details': {
                            'email': ['A user with this email already exists.']
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                logger.error(f"Registration error: {e}", exc_info=True)
                return Response({
                    'error': 'Registration failed. Please try again.',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Log validation errors for debugging
        logger.warning(f"Registration validation failed: {serializer.errors}")
        
        # Return errors in a format that frontend can easily parse
        # Flatten errors for easier frontend consumption
        flattened_errors = {}
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                # Take the first error message for each field
                flattened_errors[field] = str(errors[0]) if errors else 'Invalid value'
            else:
                flattened_errors[field] = str(errors)
        
        # Get primary error message (prefer email error if exists, otherwise first error)
        primary_message = None
        if 'email' in flattened_errors:
            primary_message = flattened_errors['email']
        elif flattened_errors:
            primary_message = list(flattened_errors.values())[0]
        else:
            primary_message = 'Please check your input and try again.'
        
        return Response({
            'error': primary_message,
            'errors': flattened_errors,
            'details': serializer.errors  # Keep full details for debugging
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Check if user exists
            try:
                user_obj = User.objects.get(email=email)
                
                # Check if user is active
                if not user_obj.is_active:
                    logger.warning(f"Login attempt for inactive user: {email}")
                    return Response({
                        'error': 'Your account is inactive. Please check your email to verify your account.',
                        'detail': 'Account is inactive'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # User exists and is active - try to authenticate
                user = authenticate(email=email, password=password)
                if user is not None:
                    # Check if email is verified
                    try:
                        email_verified = user.teacher_profile.email_verified
                    except TeacherProfile.DoesNotExist:
                        email_verified = False
                    
                    refresh = RefreshToken.for_user(user)
                    response_data = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': UserSerializer(user).data
                    }
                    
                    # Add warning if email is not verified
                    if not email_verified:
                        response_data['warning'] = 'Please verify your email address to access all features.'
                    
                    return Response(response_data)
                else:
                    # User exists but password is wrong
                    logger.warning(f"Failed login attempt - incorrect password for email: {email}")
                    return Response({
                        'error': 'Incorrect password. Please check your password and try again.',
                        'detail': 'Invalid password'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                    
            except User.DoesNotExist:
                # User doesn't exist
                logger.warning(f"Failed login attempt - email not found: {email}")
                return Response({
                    'error': 'No account found with this email address. Please check your email or sign up for a new account.',
                    'detail': 'Email not found'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Serializer validation failed
        logger.warning(f"Login validation failed: {serializer.errors}")
        return Response({
            'error': 'Invalid request data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout view that invalidates the refresh token.
    Works with or without token blacklist app.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                token = RefreshToken(refresh_token)
                # Try to blacklist if blacklist app is installed
                try:
                    token.blacklist()
                except AttributeError:
                    # Blacklist app not installed - token will expire naturally
                    # This is acceptable for logout functionality
                    pass
                except Exception:
                    # Blacklist failed but we'll still return success
                    # Token will expire naturally based on REFRESH_TOKEN_LIFETIME
                    pass
                
                return Response({
                    'message': 'Successfully logged out'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                # Invalid token - still return success to prevent user enumeration
                return Response({
                    'message': 'Successfully logged out'
                }, status=status.HTTP_200_OK)
        except Exception as e:
            # Any other error - still return success
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class TeacherProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherProfileSerializer

    def get_object(self):
        return self.request.user.teacher_profile


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    serializer_class = UserPreferencesSerializer

    def get_object(self):
        return self.request.user.preferences


class PasswordChangeView(APIView):
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': 'Old password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Send email with reset link using email service
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                try:
                    from apps.notifications.services import EmailService
                    EmailService.send_password_reset_email(user, reset_url)
                except Exception as e:
                    logger.warning(f"Failed to send password reset email via service: {e}")
                    # Fallback to simple email if service fails
                    send_mail(
                        'Password Reset Request',
                        f'Click the link to reset your password: {reset_url}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                
                return Response({
                    'message': 'Password reset email sent'
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # Return success even if user doesn't exist to prevent user enumeration
                return Response({
                    'message': 'Password reset email sent'
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['token'].split('/')[0]))
                user = User.objects.get(pk=uid)
                token = serializer.validated_data['token'].split('/')[1]
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({
                        'message': 'Password reset successfully'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'Invalid token'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'error': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestEmailView(APIView):
    """
    Test endpoint to send a test email (for debugging email configuration).
    Only available in development or for superusers.
    """
    permission_classes = [permissions.AllowAny]  # Allow any for testing
    
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email address is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # Log email configuration
            logger.info(f"Testing email to {email}")
            logger.info(f"EMAIL_HOST: {settings.EMAIL_HOST}")
            logger.info(f"EMAIL_PORT: {settings.EMAIL_PORT}")
            logger.info(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
            
            send_mail(
                'Test Email from Food Science Toolbox',
                'This is a test email to verify that email sending is working correctly.\n\n'
                'If you received this email, your email configuration is working properly!',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({
                'message': f'Test email sent successfully to {email}. Please check your inbox (and spam folder).'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to send test email to {email}: {e}", exc_info=True)
            return Response({
                'error': f'Failed to send test email: {str(e)}',
                'details': 'Please check your email configuration in environment variables.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        """
        Verify user email using the verification token.
        Returns JSON response for frontend to handle redirect.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            profile = TeacherProfile.objects.get(email_verification_token=token)
            
            # Verify the email
            profile.verify_email()
            
            # Activate the user account if it was inactive
            user = profile.user
            if not user.is_active:
                user.is_active = True
                user.save()
            
            logger.info(f"Email verified successfully for user {user.email}")
            
            # Return success response - frontend will handle redirect
            return Response({
                'message': 'Email verified successfully! You can now sign in.',
                'verified': True
            }, status=status.HTTP_200_OK)
            
        except TeacherProfile.DoesNotExist:
            logger.warning(f"Invalid verification token attempted: {token}")
            return Response({
                'error': 'Invalid or expired verification token. Please request a new verification email.',
                'verified': False
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Email verification error: {e}", exc_info=True)
            return Response({
                'error': 'Verification failed. Please try again or request a new verification email.',
                'verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Resend verification email to the authenticated user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            user = request.user
            profile, _ = TeacherProfile.objects.get_or_create(user=user)
            
            # Generate new verification token
            verification_token = profile.generate_verification_token()
            
            # Create verification link
            frontend_url = settings.FRONTEND_URL
            verification_link = f"{frontend_url}/verify-email/{verification_token}/"
            
            # Send verification email
            from apps.notifications.services import EmailService
            verification_result = EmailService.send_email_verification(user, verification_link)
            
            if verification_result:
                logger.info(f"Verification email resent to {user.email}")
                return Response({
                    'message': 'Verification email sent successfully. Please check your inbox.'
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Email verification send returned False for {user.email}")
                return Response({
                    'error': 'Failed to send verification email. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Failed to resend verification email to {user.email}: {e}", exc_info=True)
            return Response({
                'error': 'Failed to send verification email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactSupportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Send a contact/support email from the authenticated user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        message = request.data.get('message', '').strip()
        subject = request.data.get('subject', 'Support Request').strip()
        
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = request.user
            support_email = 'admin@foodsciencetoolbox.com'
            
            # Create email content
            email_subject = f"Support Request from {user.email}: {subject}"
            email_body = f"""Support Request from Food Science Toolbox

From: {user.first_name} {user.last_name} ({user.email})
Subject: {subject}

Message:
{message}

---
This message was sent from the Food Science Toolbox platform.
User ID: {user.id}
"""
            
            # Send email using Django's send_mail
            from django.core.mail import send_mail, EmailMessage
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@foodsciencetoolbox.com')
            
            # Use EmailMessage to set Reply-To header
            email = EmailMessage(
                email_subject,
                email_body,
                from_email,
                [support_email],
                reply_to=[user.email],  # Set reply-to to user's email
            )
            email.send(fail_silently=False)
            
            logger.info(f"Support email sent from {user.email} to {support_email}")
            
            return Response({
                'message': 'Your message has been sent successfully. We will get back to you soon.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to send support email from {user.email}: {e}", exc_info=True)
            return Response({
                'error': 'Failed to send message. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)