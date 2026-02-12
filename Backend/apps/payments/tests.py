from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .models import StripeCustomer, PaymentHistory

User = get_user_model()


class PaymentAPITest(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('apps.payments.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_stripe_session):
        # Mock Stripe response
        mock_stripe_session.return_value = {
            'id': 'cs_test_123',
            'url': 'https://checkout.stripe.com/test'
        }
        
        # Make request
        response = self.client.post(reverse('payments:create-checkout-session'), {
            'price_id': 'price_123',
            'success_url': 'https://example.com/success',
            'cancel_url': 'https://example.com/cancel'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('checkout_session_id', response.data)
        self.assertIn('checkout_url', response.data)
        
    def test_create_payment_intent_missing_amount(self):
        # Make request without amount
        response = self.client.post(reverse('payments:create-payment-intent'), {
            'currency': 'usd',
            'description': 'Test payment'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    @patch('apps.payments.stripe_service.stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_stripe_intent):
        # Mock Stripe response
        mock_stripe_intent.return_value = {
            'id': 'pi_123',
            'client_secret': 'secret_123'
        }
        
        # Make request
        response = self.client.post(reverse('payments:create-payment-intent'), {
            'amount': 9.99,
            'currency': 'usd',
            'description': 'Test payment'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('client_secret', response.data)
        self.assertIn('payment_intent_id', response.data)
        
    def test_payment_history_list(self):
        # Create payment history
        PaymentHistory.objects.create(
            user=self.user,
            stripe_payment_intent_id='pi_123',
            amount=9.99,
            currency='usd',
            status='succeeded',
            description='Test payment'
        )
        
        # Make request
        response = self.client.get(reverse('payments:payment-history'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '9.99')