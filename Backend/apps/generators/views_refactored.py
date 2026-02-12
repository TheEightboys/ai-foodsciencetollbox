"""
Refactored views module using centralized error handling.
Eliminates duplicate error handling patterns.
"""

import logging
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db import transaction

from .error_handling import handle_generator_errors, ErrorHandler
from .exceptions_unified import (
    GenerationLimitError,
    ValidationError,
    DatabaseError
)
from .serializers import (
    LessonStarterGenerateSerializer,
    LearningObjectivesGenerateSerializer,
    DiscussionQuestionsGenerateSerializer,
    QuizGenerateSerializer
)
from .models import GeneratedContent
from apps.memberships.services import GenerationLimitService
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


class BaseGenerateView(APIView):
    """
    Base view for all generation endpoints.
    Implements common patterns to eliminate duplication.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = None
    generator_function = None
    content_type = None
    
    @handle_generator_errors
    def post(self, request):
        """
        Handle generation requests with consistent error handling.
        """
        # Check API key configuration
        self._check_api_key()
        
        # Validate generation limit
        self._validate_generation_limit(request.user)
        
        # Validate and serialize input
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return ErrorHandler.handle_validation_error(serializer.errors)
        
        # Generate content
        result = self._generate_content(request.user, serializer.validated_data)
        
        # Save to database
        saved_content = self._save_content(request.user, serializer.validated_data, result)
        
        # Increment generation count
        self._increment_generation_count(request.user)
        
        # Return response
        return self._build_response(saved_content, result)
    
    def _check_api_key(self):
        """Check if API key is configured."""
        from django.conf import settings
        if not settings.OPENAI_API_KEY:
            raise ValidationError(
                "OpenAI API key is not configured. Please contact support.",
                setting="OPENAI_API_KEY"
            )
    
    def _validate_generation_limit(self, user):
        """Validate user's generation limit."""
        try:
            GenerationLimitService.validate_limit(user)
        except ValidationError as e:
            raise GenerationLimitError(str(e))
    
    def _generate_content(self, user, validated_data):
        """Generate content using the appropriate service."""
        service = OpenAIService()
        generator_func = getattr(service, self.generator_function)
        
        # Add user preferences if available
        try:
            tone = user.preferences.preferred_tone
        except AttributeError:
            tone = 'professional'
        
        return generator_func(tone=tone, **validated_data)
    
    def _save_content(self, user, validated_data, result):
        """Save generated content to database."""
        try:
            with transaction.atomic():
                return GeneratedContent.objects.create(
                    user=user,
                    content_type=self.content_type,
                    title=self._generate_title(validated_data),
                    content=result['content'],
                    input_parameters=validated_data,
                    tokens_used=result.get('tokens_used', 0),
                    generation_time=result.get('generation_time', 0)
                )
        except Exception as e:
            logger.error(f"Failed to save content: {e}", exc_info=True)
            raise DatabaseError("Failed to save generated content")
    
    def _increment_generation_count(self, user):
        """Increment user's generation count."""
        try:
            GenerationLimitService.increment_count(user)
        except Exception as e:
            logger.warning(f"Failed to increment generation count: {e}")
            # Don't fail the request
    
    def _generate_title(self, validated_data):
        """Generate a title for the content."""
        topic = validated_data.get('topic', 'Generated Content')
        return f"{self.content_type.title()}: {topic}"
    
    def _build_response(self, saved_content, result):
        """Build the response object."""
        from django.conf import settings
        
        response_data = {
            'id': saved_content.id,
            'content': result['content'],
            'tokens_used': result.get('tokens_used', 0),
            'generation_time': result.get('generation_time', 0),
            'created_at': saved_content.created_at
        }
        
        # Add download URLs
        response_data.update({
            'pdf_url': f'/api/generators/{saved_content.id}/export/pdf/',
            'docx_url': f'/api/generators/{saved_content.id}/export/docx/'
        })
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class LessonStarterGenerateView(BaseGenerateView):
    """View for generating lesson starters."""
    serializer_class = LessonStarterGenerateSerializer
    generator_function = 'generate_lesson_starter'
    content_type = 'lesson_starter'


class LearningObjectivesGenerateView(BaseGenerateView):
    """View for generating learning objectives."""
    serializer_class = LearningObjectivesGenerateSerializer
    generator_function = 'generate_learning_objectives'
    content_type = 'learning_objectives'


class DiscussionQuestionsGenerateView(BaseGenerateView):
    """View for generating discussion questions."""
    serializer_class = DiscussionQuestionsGenerateSerializer
    generator_function = 'generate_discussion_questions'
    content_type = 'discussion_questions'


class QuizGenerateView(BaseGenerateView):
    """View for generating quizzes."""
    serializer_class = QuizGenerateSerializer
    generator_function = 'generate_quiz'
    content_type = 'quiz'


class ContentListView(APIView):
    """
    View for listing user's generated content.
    Uses centralized error handling.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @handle_generator_errors
    def get(self, request):
        """List user's content."""
        queryset = GeneratedContent.objects.filter(user=request.user)
        
        # Apply filters
        queryset = self._apply_filters(queryset, request)
        
        # Order by creation date
        queryset = queryset.order_by('-created_at')
        
        # Serialize and return
        serializer = self._get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def _apply_filters(self, queryset, request):
        """Apply filters to queryset."""
        # Filter by content type
        content_type = request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Filter by favorites
        favorites_only = request.query_params.get('favorites', '').lower() == 'true'
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)
        
        return queryset
    
    def _get_serializer(self, *args, **kwargs):
        """Get appropriate serializer."""
        from .serializers import GeneratedContentSerializer
        return GeneratedContentSerializer(*args, **kwargs)


class ContentDetailView(APIView):
    """
    View for retrieving a single content item.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @handle_generator_errors
    def get(self, request, pk):
        """Get a specific content item."""
        content = get_object_or_404(GeneratedContent, pk=pk, user=request.user)
        
        from .serializers import GeneratedContentDetailSerializer
        serializer = GeneratedContentDetailSerializer(content)
        
        return Response(serializer.data)


class ToggleFavoriteView(APIView):
    """
    View for toggling favorite status.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @handle_generator_errors
    def post(self, request, pk):
        """Toggle favorite status."""
        content = get_object_or_404(GeneratedContent, pk=pk, user=request.user)
        
        try:
            content.is_favorite = not content.is_favorite
            content.save(update_fields=['is_favorite', 'updated_at'])
        except Exception as e:
            logger.error(f"Failed to toggle favorite: {e}", exc_info=True)
            raise DatabaseError("Failed to update favorite status")
        
        return Response({
            'is_favorite': content.is_favorite,
            'message': 'Content updated successfully'
        })


class DeleteContentView(APIView):
    """
    View for deleting content.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @handle_generator_errors
    def delete(self, request, pk):
        """Delete a content item."""
        content = get_object_or_404(GeneratedContent, pk=pk, user=request.user)
        
        try:
            content.delete()
        except Exception as e:
            logger.error(f"Failed to delete content: {e}", exc_info=True)
            raise DatabaseError("Failed to delete content")
        
        return Response({
            'message': 'Content deleted successfully'
        })


# Export views
__all__ = [
    'LessonStarterGenerateView',
    'LearningObjectivesGenerateView',
    'DiscussionQuestionsGenerateView',
    'QuizGenerateView',
    'ContentListView',
    'ContentDetailView',
    'ToggleFavoriteView',
    'DeleteContentView',
]
