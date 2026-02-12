from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.memberships.models import MembershipTier, UserMembership
from apps.payments.models import PaymentHistory
from apps.generators.models import GeneratedContent

User = get_user_model()


class AdminDashboardAPITest(TestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        # Create membership tier
        self.starter_tier = MembershipTier.objects.create(
            name='starter',
            display_name='Starter',
            monthly_price=0.00,
            generation_limit=50
        )
        
        # Create user membership
        self.user_membership = UserMembership.objects.create(
            user=self.regular_user,
            tier=self.starter_tier
        )
        
        # Create API client
        self.client = APIClient()

    def test_admin_can_access_dashboard_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('admin_dashboard:dashboard-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_regular_user_cannot_access_dashboard_stats(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('admin_dashboard:dashboard-stats'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_unauthenticated_user_cannot_access_dashboard_stats(self):
        response = self.client.get(reverse('admin_dashboard:dashboard-stats'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminDashboardDataTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create test data
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='userpass123',
            first_name='User',
            last_name='One'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='userpass123',
            first_name='User',
            last_name='Two'
        )
        
        # Create membership tier
        self.starter_tier = MembershipTier.objects.create(
            name='starter',
            display_name='Starter',
            monthly_price=0.00,
            generation_limit=50
        )
        
        # Create user memberships
        UserMembership.objects.create(user=self.user1, tier=self.starter_tier)
        UserMembership.objects.create(user=self.user2, tier=self.starter_tier)
        
        # Create payment history
        PaymentHistory.objects.create(
            user=self.user1,
            stripe_payment_intent_id='pi_123',
            amount=9.99,
            currency='usd',
            status='succeeded'
        )
        
        # Create generated content
        GeneratedContent.objects.create(
            user=self.user1,
            content_type='lesson_starter',
            title='Test Lesson Starter',
            content='Test content'
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_dashboard_stats_endpoint(self):
        response = self.client.get(reverse('admin_dashboard:dashboard-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response contains the expected data structure
        self.assertIn('stats', response.data)
        self.assertIn('recent_users', response.data)
        self.assertIn('recent_payments', response.data)
        self.assertIn('recent_content', response.data)
        
        # Check stats counts
        self.assertEqual(response.data['stats']['total_users'], 3)  # admin + 2 regular users
        self.assertEqual(response.data['stats']['total_payments'], 1)
        self.assertEqual(response.data['stats']['total_generated_content'], 1)
        
        # Check recent data
        self.assertEqual(len(response.data['recent_users']), 2)  # Limited to 5, but only 2 regular users
        self.assertEqual(len(response.data['recent_payments']), 1)
        self.assertEqual(len(response.data['recent_content']), 1)