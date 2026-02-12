from django.test import TestCase
from .utils import generate_random_token, calculate_reading_time, format_currency
from .decorators import require_membershipTier


class CoreUtilsTest(TestCase):
    def test_generate_random_token(self):
        token = generate_random_token()
        self.assertEqual(len(token), 32)
        self.assertIsInstance(token, str)
        
        # Test with custom length
        token = generate_random_token(16)
        self.assertEqual(len(token), 16)

    def test_calculate_reading_time(self):
        # Test with short text
        text = "This is a short sentence."
        reading_time = calculate_reading_time(text)
        self.assertEqual(reading_time, 0)  # Less than 1 minute
        
        # Test with longer text (200 words should be 1 minute)
        text = "word " * 200
        reading_time = calculate_reading_time(text)
        self.assertEqual(reading_time, 1)
        
        # Test with very long text (450 words should be 2 minutes at 200 wpm)
        text = "word " * 450
        reading_time = calculate_reading_time(text)
        self.assertEqual(reading_time, 2)

    def test_format_currency(self):
        # Test USD formatting
        amount = 9.99
        formatted = format_currency(amount, 'USD')
        self.assertEqual(formatted, '$9.99')
        
        # Test other currency formatting
        amount = 9.99
        formatted = format_currency(amount, 'EUR')
        self.assertEqual(formatted, '9.99 EUR')


class CoreDecoratorsTest(TestCase):
    def test_require_membership_tier_decorator(self):
        # This is a basic test to ensure the decorator function exists
        # Actual testing of decorator logic would require more complex setup
        self.assertIsNotNone(require_membershipTier)