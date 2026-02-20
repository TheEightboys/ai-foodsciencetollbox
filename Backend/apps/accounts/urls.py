from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    TeacherProfileView,
    UserPreferencesView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerificationView,
    ResendVerificationEmailView,
    ContactSupportView,
    TestEmailView
)
from .google_oauth import GoogleLoginView, GoogleCallbackView, GoogleCodeExchangeView
from .supabase_views import SupabaseTokenExchangeView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('teacher-profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('preferences/', UserPreferencesView.as_view(), name='user-preferences'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('reset-password/', PasswordResetRequestView.as_view(), name='reset-password-request'),
    path('reset-password-confirm/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
    path('verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification-email/', ResendVerificationEmailView.as_view(), name='resend-verification-email'),
    path('contact-support/', ContactSupportView.as_view(), name='contact-support'),
    path('test-email/', TestEmailView.as_view(), name='test-email'),
    # Supabase token exchange (primary auth method)
    path('supabase-token/', SupabaseTokenExchangeView.as_view(), name='supabase-token'),
    # Google OAuth (legacy — kept for backwards compat)
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-callback'),
    # Google OAuth code exchange — frontend handles redirect, posts code here
    path('google/exchange/', GoogleCodeExchangeView.as_view(), name='google-exchange'),
]