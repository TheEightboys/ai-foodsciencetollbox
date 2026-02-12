from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .models import TeacherProfile, UserPreferences

User = get_user_model()


class AccountAPITest(TestCase):
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

    def test_user_registration_success(self):
        # Make request
        response = self.client.post(reverse('accounts:register'), {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        
        # Check that user was created
        self.assertEqual(User.objects.count(), 2)
        new_user = User.objects.get(email='newuser@example.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
        
        # Check that profile and preferences were created
        self.assertTrue(hasattr(new_user, 'teacher_profile'))
        self.assertTrue(hasattr(new_user, 'preferences'))
        
    def test_user_registration_password_mismatch(self):
        # Make request with mismatched passwords
        response = self.client.post(reverse('accounts:register'), {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'differentpass123'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
        
    def test_user_login_success(self):
        # Make request
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
    def test_user_login_invalid_credentials(self):
        # Make request with invalid credentials
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@example.com',
            'password': 'wrongpass123'
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        
    def test_user_profile_retrieve_update(self):
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        # Make GET request
        response = self.client.get(reverse('accounts:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        
        # Make PUT request to update
        response = self.client.put(reverse('accounts:user-profile'), {
            'first_name': 'Updated',
            'last_name': 'Name'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        
        # Refresh user from database and check
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        
    def test_teacher_profile_retrieve_update(self):
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        # Make GET request
        response = self.client.get(reverse('accounts:teacher-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_academy_member'])
        
        # Make PUT request to update
        response = self.client.put(reverse('accounts:teacher-profile'), {
            'is_academy_member': True
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_academy_member'])
        
        # Refresh profile from database and check
        self.user.teacher_profile.refresh_from_db()
        self.assertTrue(self.user.teacher_profile.is_academy_member)
        
    def test_user_preferences_retrieve_update(self):
        # Authenticate user
        self.client.force_authenticate(user=self.user)
        
        # Make GET request
        response = self.client.get(reverse('accounts:user-preferences'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['preferred_grade_level'], 'high_school')
        
        # Make PUT request to update
        response = self.client.put(reverse('accounts:user-preferences'), {
            'preferred_grade_level': 'middle_school',
            'preferred_subject': 'consumer_science'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['preferred_grade_level'], 'middle_school')
        self.assertEqual(response.data['preferred_subject'], 'consumer_science')
        
        # Refresh preferences from database and check
        self.user.preferences.refresh_from_db()
        self.assertEqual(self.user.preferences.preferred_grade_level, 'middle_school')
        self.assertEqual(self.user.preferences.preferred_subject, 'consumer_science')