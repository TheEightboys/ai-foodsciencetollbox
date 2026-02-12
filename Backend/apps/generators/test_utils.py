"""
Consolidated test utilities for the generators app.
Eliminates duplicate mock classes and test helpers.
"""

import json
from typing import List, Dict, Any, Optional
from unittest.mock import Mock
from apps.generators.shared.llm_client import LLMClient


class MockLLMClient(LLMClient):
    """
    Unified mock LLM client for testing.
    Replaces duplicate implementations across test files.
    """
    
    def __init__(self, responses: List[str] = None, default_response: str = "Test response"):
        """
        Initialize mock client.
        
        Args:
            responses: List of responses to return in sequence
            default_response: Default response if no responses list provided
        """
        self.responses = responses or [default_response]
        self.call_count = 0
        self.call_history = []
        self.raise_error = None
        self.raise_on_call = None
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate mock response.
        
        Args:
            prompt: The prompt (recorded for testing)
            
        Returns:
            Mock response
        """
        self.call_count += 1
        self.call_history.append(prompt)
        
        # Check if we should raise an error
        if self.raise_on_call and self.call_count >= self.raise_on_call:
            raise self.raise_error or Exception("Mock error")
        
        # Return response from list or default
        if self.call_count <= len(self.responses):
            return self.responses[self.call_count - 1]
        else:
            return self.responses[-1] if self.responses else "Default response"
    
    def reset(self):
        """Reset the mock state."""
        self.call_count = 0
        self.call_history = []
        self.raise_error = None
        self.raise_on_call = None
    
    def set_error(self, error: Exception, on_call: Optional[int] = None):
        """
        Set an error to raise on a specific call.
        
        Args:
            error: Exception to raise
            on_call: Call number to raise on (None for immediate)
        """
        self.raise_error = error
        self.raise_on_call = on_call
    
    def get_last_prompt(self) -> str:
        """Get the last prompt sent to the client."""
        return self.call_history[-1] if self.call_history else None
    
    def assert_prompt_contains(self, text: str):
        """Assert that the last prompt contains specific text."""
        last_prompt = self.get_last_prompt()
        assert last_prompt is not None, "No prompts sent"
        assert text in last_prompt, f"Prompt '{last_prompt}' does not contain '{text}'"


class MockOpenAIClient:
    """
    Mock OpenAI client for testing OpenAI-specific functionality.
    """
    
    def __init__(self, responses: List[Dict] = None):
        """
        Initialize mock OpenAI client.
        
        Args:
            responses: List of response dictionaries
        """
        self.responses = responses or []
        self.call_count = 0
        self.chat = self
        self.completions = self
    
    def create(self, *args, **kwargs):
        """Mock create method."""
        response = Mock()
        
        if self.call_count < len(self.responses):
            mock_response = self.responses[self.call_count]
        else:
            mock_response = {
                'choices': [{'message': {'content': 'Default response'}}],
                'usage': {'total_tokens': 100}
            }
        
        # Set up mock response object
        response.choices = []
        for choice in mock_response.get('choices', []):
            choice_mock = Mock()
            choice_mock.message = Mock()
            choice_mock.message.content = choice.get('message', {}).get('content', '')
            response.choices.append(choice_mock)
        
        response.usage = Mock()
        response.usage.total_tokens = mock_response.get('usage', {}).get('total_tokens', 0)
        
        self.call_count += 1
        return response


class TestDataFactory:
    """
    Factory for creating test data.
    Eliminates duplicate test data creation.
    """
    
    @staticmethod
    def create_lesson_starter_data(**overrides) -> Dict[str, Any]:
        """Create lesson starter test data."""
        default_data = {
            'subject': 'Science',
            'grade_level': 'High School',
            'topic': 'Photosynthesis',
            'duration_minutes': 45,
            'tone': 'professional',
            'customization': ''
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_learning_objectives_data(**overrides) -> Dict[str, Any]:
        """Create learning objectives test data."""
        default_data = {
            'user_intent': 'Create learning objectives for photosynthesis',
            'grade_level': 'High School',
            'num_objectives': 5
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_discussion_questions_data(**overrides) -> Dict[str, Any]:
        """Create discussion questions test data."""
        default_data = {
            'subject': 'Science',
            'topic': 'Climate Change',
            'grade_level': 'High School',
            'num_questions': 5,
            'customization': ''
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_quiz_data(**overrides) -> Dict[str, Any]:
        """Create quiz test data."""
        default_data = {
            'subject': 'Science',
            'grade_level': 'High School',
            'topic': 'Photosynthesis',
            'number_of_questions': 10,
            'question_types': ['Multiple Choice', 'True/False'],
            'tone': 'balanced'
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_user(**overrides):
        """Create a test user."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        default_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        default_user.update(overrides)
        
        return User.objects.create_user(**default_user)


class AssertionHelpers:
    """
    Helper methods for common test assertions.
    """
    
    @staticmethod
    def assert_valid_response(response, expected_status: int = 200):
        """Assert response has valid structure."""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        
        if hasattr(response, 'data'):
            assert isinstance(response.data, (dict, list)), "Response data should be dict or list"
    
    @staticmethod
    def assert_error_response(response, expected_error_code: str, expected_status: int = 400):
        """Assert error response has correct structure."""
        AssertionHelpers.assert_valid_response(response, expected_status)
        
        assert 'error' in response.data, "Error response should have 'error' field"
        assert 'error_code' in response.data, "Error response should have 'error_code' field"
        assert response.data['error_code'] == expected_error_code, f"Expected error code {expected_error_code}, got {response.data['error_code']}"
    
    @staticmethod
    def assert_content_saved(user, content_type: str, expected_count: int = 1):
        """Assert content was saved to database."""
        from apps.generators.models import GeneratedContent
        
        contents = GeneratedContent.objects.filter(
            user=user,
            content_type=content_type
        )
        
        assert contents.count() == expected_count, f"Expected {expected_count} contents, found {contents.count()}"
    
    @staticmethod
    def assert_cache_hit(cache_key: str):
        """Assert a cache key exists."""
        from django.core.cache import cache
        
        value = cache.get(cache_key)
        assert value is not None, f"Cache key {cache_key} not found"
    
    @staticmethod
    def assert_log_contains(caplog, expected_message: str, level: str = 'ERROR'):
        """Assert log contains expected message."""
        for record in caplog.records:
            if record.levelname == level and expected_message in record.message:
                return
        
        assert False, f"Log message '{expected_message}' not found at level {level}"


class CacheTestHelper:
    """
    Helper for testing cache functionality.
    """
    
    @staticmethod
    def clear_cache():
        """Clear all cache."""
        from django.core.cache import cache
        cache.clear()
    
    @staticmethod
    def set_cache_value(key: str, value: Any, timeout: int = 300):
        """Set a cache value."""
        from django.core.cache import cache
        cache.set(key, value, timeout)
    
    @staticmethod
    def get_cache_value(key: str):
        """Get a cache value."""
        from django.core.cache import cache
        return cache.get(key)
    
    @staticmethod
    def assert_cache_exists(key: str):
        """Assert cache key exists."""
        from django.core.cache import cache
        assert cache.get(key) is not None, f"Cache key {key} does not exist"
    
    @staticmethod
    def assert_cache_missing(key: str):
        """Assert cache key does not exist."""
        from django.core.cache import cache
        assert cache.get(key) is None, f"Cache key {key} exists but shouldn't"


class APITestHelper:
    """
    Helper for API testing.
    """
    
    @staticmethod
    def create_authenticated_client(user):
        """Create an authenticated API client."""
        from rest_framework.test import APIClient
        
        client = APIClient()
        client.force_authenticate(user=user)
        return client
    
    @staticmethod
    def post_json(client, url: str, data: Dict[str, Any], **kwargs):
        """Post JSON data to API."""
        return client.post(url, data, format='json', **kwargs)
    
    @staticmethod
    def assert_json_schema(response_data: Dict[str, Any], required_fields: List[str]):
        """Assert JSON response contains required fields."""
        for field in required_fields:
            assert field in response_data, f"Required field '{field}' missing from response"


# Base test class with common functionality
class BaseGeneratorTestCase:
    """
    Base test case for generator tests.
    Provides common setup and utilities.
    """
    
    def setUp(self):
        """Set up common test data."""
        self.user = TestDataFactory.create_user()
        self.client = APITestHelper.create_authenticated_client(self.user)
        self.mock_llm = MockLLMClient()
        CacheTestHelper.clear_cache()
    
    def tearDown(self):
        """Clean up after tests."""
        CacheTestHelper.clear_cache()
    
    def create_lesson_starter(self, **overrides):
        """Create a lesson starter through API."""
        data = TestDataFactory.create_lesson_starter_data(**overrides)
        return APITestHelper.post_json(self.client, '/api/generators/lesson_starter/generate/', data)
    
    def create_learning_objectives(self, **overrides):
        """Create learning objectives through API."""
        data = TestDataFactory.create_learning_objectives_data(**overrides)
        return APITestHelper.post_json(self.client, '/api/generators/learning_objectives/generate/', data)
    
    def create_discussion_questions(self, **overrides):
        """Create discussion questions through API."""
        data = TestDataFactory.create_discussion_questions_data(**overrides)
        return APITestHelper.post_json(self.client, '/api/generators/discussion_questions/generate/', data)
    
    def create_quiz(self, **overrides):
        """Create a quiz through API."""
        data = TestDataFactory.create_quiz_data(**overrides)
        return APITestHelper.post_json(self.client, '/api/generators/quiz/generate/', data)


# Export all utilities
__all__ = [
    'MockLLMClient',
    'MockOpenAIClient',
    'TestDataFactory',
    'AssertionHelpers',
    'CacheTestHelper',
    'APITestHelper',
    'BaseGeneratorTestCase',
]
