from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import MembershipTier, UserMembership

User = get_user_model()


class MembershipAPITest(TestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create membership tiers
        self.starter_tier = MembershipTier.objects.create(
            name='starter',
            display_name='Starter',
            monthly_price=0.00,
            generation_limit=50
        )
        
        self.pro_tier = MembershipTier.objects.create(
            name='pro',
            display_name='Pro',
            monthly_price=9.99,
            generation_limit=500
        )
        
        # Create user membership
        self.user_membership = UserMembership.objects.create(
            user=self.user,
            tier=self.starter_tier,
            generations_used_this_month=10
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_membership_tier_list(self):
        # Make request
        response = self.client.get(reverse('memberships:tier-list'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'starter')
        self.assertEqual(response.data[1]['name'], 'pro')
        
    def test_user_membership_detail(self):
        # Make request
        response = self.client.get(reverse('memberships:membership-detail'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tier']['name'], 'starter')
        self.assertEqual(response.data['generations_used_this_month'], 10)
        
    def test_membership_upgrade(self):
        # Make request to upgrade to pro tier
        response = self.client.post(reverse('memberships:membership-upgrade'), {
            'tier_id': self.pro_tier.id
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('membership', response.data)
        
        # Refresh membership from database and check
        self.user_membership.refresh_from_db()
        self.assertEqual(self.user_membership.tier, self.pro_tier)
        
    def test_membership_upgrade_invalid_tier(self):
        # Make request with invalid tier ID
        response = self.client.post(reverse('memberships:membership-upgrade'), {
            'tier_id': 999
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_usage_stats(self):
        # Make request
        response = self.client.get(reverse('memberships:usage-stats'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_generate_content'])
        self.assertEqual(response.data['generations_used'], 10)
        self.assertEqual(response.data['remaining_generations'], 40)
        self.assertEqual(response.data['tier_limit'], 50)
        self.assertEqual(response.data['tier_name'], 'Starter')