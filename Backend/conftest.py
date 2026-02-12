import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.memberships.models import MembershipTier

User = get_user_model()


@pytest.fixture
def api_client():
    """A Django REST framework API client instance."""
    return APIClient()


@pytest.fixture
def user(db):
    """A regular user instance."""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    """An admin user instance."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def membership_tier(db):
    """A membership tier instance."""
    return MembershipTier.objects.create(
        name='starter',
        display_name='Starter',
        monthly_price=0.00,
        generation_limit=50
    )


@pytest.fixture
def authenticated_api_client(api_client, user):
    """An authenticated API client with a regular user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_user):
    """An authenticated API client with an admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client