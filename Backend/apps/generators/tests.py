from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .models import GeneratedContent

User = get_user_model()


class GeneratorAPITest(TestCase):
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

    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_generate_lesson_starter_success(self, mock_openai):
        # Mock OpenAI response
        mock_openai.return_value.chat.completions.create.return_value = {
            'choices': [{'message': {'content': 'Test lesson starter content'}}],
            'usage': {'total_tokens': 100}
        }
        
        # Make request
        response = self.client.post(reverse('generators:lesson-starter-generate'), {
            'subject': 'food_science',
            'grade_level': 'high_school',
            'topic': 'Nutrition',
            'duration_minutes': 10
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('content', response.data)
        self.assertIn('tokens_used', response.data)
        
        # Check that content was saved to database
        self.assertEqual(GeneratedContent.objects.count(), 1)
        generated_content = GeneratedContent.objects.first()
        self.assertEqual(generated_content.content_type, 'lesson_starter')
        self.assertEqual(generated_content.title, 'Lesson Starter: Nutrition')
        
    def test_generate_lesson_starter_invalid_data(self):
        # Make request with invalid data
        response = self.client.post(reverse('generators:lesson-starter-generate'), {
            'subject': 'invalid_subject',
            'grade_level': 'high_school',
            'topic': 'Nutrition',
            'duration_minutes': 10
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_generate_learning_objectives_success(self, mock_openai):
        # Mock OpenAI response
        mock_openai.return_value.chat.completions.create.return_value = {
            'choices': [{'message': {'content': 'Test learning objectives content'}}],
            'usage': {'total_tokens': 100}
        }
        
        # Make request
        response = self.client.post(reverse('generators:learning-objectives-generate'), {
            'subject': 'food_science',
            'grade_level': 'high_school',
            'topic': 'Nutrition',
            'number_of_objectives': 3
        })
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('content', response.data)
        
        # Check that content was saved to database
        self.assertEqual(GeneratedContent.objects.count(), 1)
        generated_content = GeneratedContent.objects.first()
        self.assertEqual(generated_content.content_type, 'learning_objectives')
        self.assertEqual(generated_content.title, 'Learning Objectives: Nutrition')
        
    def test_generated_content_list(self):
        # Create generated content
        GeneratedContent.objects.create(
            user=self.user,
            content_type='lesson_starter',
            title='Test Lesson Starter',
            content='This is a test lesson starter content.'
        )
        
        # Make request
        response = self.client.get(reverse('generators:generated-content'))
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Lesson Starter')