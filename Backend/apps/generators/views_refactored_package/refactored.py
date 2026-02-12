"""
Refactored generator views using the base class pattern.
Eliminates code duplication and provides consistent behavior.
"""

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_ratelimit.decorators import ratelimit
from ..base import BaseGenerator, GeneratorFactory, GeneratorViewMixin
from ..models import GeneratedContent
from ..serializers import (
    LessonStarterGenerateSerializer,
    LearningObjectivesGenerateSerializer,
    DiscussionQuestionsGenerateSerializer,
    QuizGenerateSerializer
)
from ..exceptions import GenerationLimitError
import logging

logger = logging.getLogger(__name__)


# Register generators with the factory
class LessonStarterGenerator(BaseGenerator):
    """Lesson starter generator implementation."""
    
    def get_content_type(self) -> str:
        return 'lesson_starter'
    
    def build_prompt(self, validated_data: dict) -> str:
        """Build lesson starter prompt."""
        # Import here to avoid circular imports
        from ..lesson_starter.prompt import build_lesson_starter_prompt
        
        return build_lesson_starter_prompt(
            subject=validated_data['subject'],
            grade_level=validated_data['grade_level'],
            topic=validated_data['topic'],
            duration_minutes=validated_data['duration_minutes'],
            tone=validated_data.get('tone', 'professional'),
            customization=validated_data.get('customization', '')
        )
    
    def validate_generated_content(self, content: str, validated_data: dict) -> tuple[bool, list]:
        """Validate lesson starter content."""
        from ..lesson_starter.validation import validate_lesson_starter
        
        return validate_lesson_starter(
            content=content,
            duration_minutes=validated_data['duration_minutes']
        )
    
    def get_serializer_class(self):
        return LessonStarterGenerateSerializer


class LearningObjectivesGenerator(BaseGenerator):
    """Learning objectives generator implementation."""
    
    def get_content_type(self) -> str:
        return 'learning_objectives'
    
    def build_prompt(self, validated_data: dict) -> str:
        """Build learning objectives prompt."""
        from ..learning_objectives.prompt import build_generation_prompt_final
        
        # Prioritize user_intent for new consolidated format
        user_intent = validated_data.get('user_intent')
        if user_intent:
            return build_generation_prompt_final(
                user_intent=user_intent,
                grade_level=validated_data['grade_level'],
                num_objectives=validated_data.get('num_objectives', 5)
            )
        
        # Fallback to legacy format
        return build_generation_prompt_final(
            user_intent=f"Create learning objectives for {validated_data.get('topic', 'the topic')}",
            grade_level=validated_data['grade_level'],
            num_objectives=validated_data.get('num_objectives', 5)
        )
    
    def validate_generated_content(self, content: str, validated_data: dict) -> tuple[bool, list]:
        """Validate learning objectives content."""
        from ..learning_objectives.validation import validate_learning_objectives_final
        
        return validate_learning_objectives_final(
            content=content,
            num_objectives=validated_data.get('num_objectives', 5),
            grade_level=validated_data['grade_level']
        )
    
    def get_serializer_class(self):
        return LearningObjectivesGenerateSerializer


class DiscussionQuestionsGenerator(BaseGenerator):
    """Discussion questions generator implementation."""
    
    def get_content_type(self) -> str:
        return 'discussion_questions'
    
    def build_prompt(self, validated_data: dict) -> str:
        """Build discussion questions prompt."""
        from ..discussion_questions.prompt import build_generation_prompt
        
        return build_generation_prompt(
            category=validated_data['subject'],
            topic=validated_data['topic'],
            grade_level=validated_data['grade_level'],
            num_questions=validated_data['num_questions'],
            teacher_details=validated_data.get('customization', '')
        )
    
    def validate_generated_content(self, content: str, validated_data: dict) -> tuple[bool, list]:
        """Validate discussion questions content."""
        from ..discussion_questions.validation import validate_discussion_questions
        
        return validate_discussion_questions(
            content=content,
            num_questions=validated_data['num_questions'],
            grade_level=validated_data['grade_level']
        )
    
    def get_serializer_class(self):
        return DiscussionQuestionsGenerateSerializer


class QuizGenerator(BaseGenerator):
    """Quiz generator implementation."""
    
    def get_content_type(self) -> str:
        return 'quiz'
    
    def build_prompt(self, validated_data: dict) -> str:
        """Build quiz prompt."""
        from ..prompt_templates import QUIZ_TEMPLATE
        
        return QUIZ_TEMPLATE.format(
            subject=validated_data['subject'],
            grade_level=validated_data['grade_level'],
            topic=validated_data['topic'],
            number_of_questions=validated_data['number_of_questions'],
            question_types=', '.join(validated_data['question_types']),
            tone=validated_data.get('tone', 'balanced')
        )
    
    def validate_generated_content(self, content: str, validated_data: dict) -> tuple[bool, list]:
        """Basic quiz validation - can be enhanced."""
        errors = []
        
        # Check if we have the expected number of questions
        expected = validated_data['number_of_questions']
        question_count = content.count('1.') + content.count('2.') + content.count('3.') + content.count('4.') + content.count('5.')
        
        if question_count < expected:
            errors.append(f'Expected {expected} questions, got {question_count}')
        
        return len(errors) == 0, errors
    
    def get_serializer_class(self):
        return QuizGenerateSerializer


# Register all generators
GeneratorFactory.register('lesson_starter', LessonStarterGenerator)
GeneratorFactory.register('learning_objectives', LearningObjectivesGenerator)
GeneratorFactory.register('discussion_questions', DiscussionQuestionsGenerator)
GeneratorFactory.register('quiz', QuizGenerator)


# Unified Generate View
class GenerateContentView(APIView, GeneratorViewMixin):
    """
    Unified view for all content generation.
    Replaces 4 separate views with one configurable view.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @method_decorator(ratelimit(key='user', rate='10/m', method='POST'))
    def post(self, request, content_type):
        """
        Generate content of the specified type.
        
        URL: /api/generators/{content_type}/generate/
        """
        # Validate content type
        if content_type not in GeneratorFactory.get_available_generators():
            return Response({
                'error': f'Unknown content type: {content_type}',
                'error_code': 'INVALID_CONTENT_TYPE',
                'available_types': GeneratorFactory.get_available_generators()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle generation
        return self.handle_generation_request(request, content_type)


# Status Check View for Async Generation
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_generation_status(request, task_id):
    """
    Check the status of an async generation task.
    
    URL: /api/generators/status/{task_id}/
    """
    try:
        generator = GeneratorFactory.create('lesson_starter')  # Any generator works
        status = generator.check_generation_status(task_id)
        
        return Response(status)
        
    except Exception as e:
        logger.error(f"Error checking generation status: {e}", exc_info=True)
        return Response({
            'error': 'Failed to check generation status',
            'error_code': 'STATUS_CHECK_FAILED'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# List Available Generators
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_headers('Authorization')
def list_generators(request):
    """
    List all available content generators.
    
    URL: /api/generators/types/
    """
    generators = GeneratorFactory.get_available_generators()
    
    generator_info = {
        'lesson_starter': {
            'name': 'Lesson Starter',
            'description': 'Generate engaging lesson starters',
            'max_duration': 60,  # minutes
            'supported_grades': ['Elementary', 'Middle', 'High', 'College']
        },
        'learning_objectives': {
            'name': 'Learning Objectives',
            'description': 'Generate measurable learning objectives',
            'max_objectives': 6,
            'supported_grades': ['Elementary', 'Middle', 'High', 'College']
        },
        'discussion_questions': {
            'name': 'Discussion Questions',
            'description': 'Generate thought-provoking discussion questions',
            'max_questions': 10,
            'supported_grades': ['Elementary', 'Middle', 'High', 'College']
        },
        'quiz': {
            'name': 'Quiz',
            'description': 'Generate quiz questions',
            'max_questions': 20,
            'question_types': ['Multiple Choice', 'True/False', 'Short Answer']
        }
    }
    
    response_data = {
        'generators': [
            {
                'type': gtype,
                **generator_info.get(gtype, {})
            }
            for gtype in generators
        ]
    }
    
    return Response(response_data)


# Legacy Views for Backward Compatibility
# These map to the new unified view but maintain old URLs

class LessonStarterGenerateView(GenerateContentView):
    """Legacy view - redirects to unified view."""
    
    def post(self, request):
        """Redirect to unified view with lesson_starter type."""
        return super().post(request, 'lesson_starter')


class LearningObjectivesGenerateView(GenerateContentView):
    """Legacy view - redirects to unified view."""
    
    def post(self, request):
        """Redirect to unified view with learning_objectives type."""
        return super().post(request, 'learning_objectives')


class DiscussionQuestionsGenerateView(GenerateContentView):
    """Legacy view - redirects to unified view."""
    
    def post(self, request):
        """Redirect to unified view with discussion_questions type."""
        return super().post(request, 'discussion_questions')


class QuizGenerateView(GenerateContentView):
    """Legacy view - redirects to unified view."""
    
    def post(self, request):
        """Redirect to unified view with quiz type."""
        return super().post(request, 'quiz')
