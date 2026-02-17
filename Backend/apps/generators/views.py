from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from .models import GeneratedContent
from .serializers import (
    GeneratedContentSerializer,
    LessonStarterGenerateSerializer,
    LearningObjectivesGenerateSerializer,
    DiscussionQuestionsGenerateSerializer,
    QuizGenerateSerializer
)
from .openai_service import OpenAIService
from .openrouter_gateway import generate_ai_content
from .shared.llm_client import OpenRouterLLMClient, get_llm_client
from .document_formatter import DocumentFormatter
from .validators import validate_generation_limit
from apps.memberships.services import GenerationLimitService
import logging

try:
    from django_ratelimit.decorators import ratelimit
except ImportError:
    # Fallback — define a no-op decorator if django-ratelimit is not installed
    def ratelimit(**_kw):
        def decorator(fn):
            return fn
        return decorator

logger = logging.getLogger(__name__)


class GenerationRateThrottle(UserRateThrottle):
    """DRF throttle: 10 generation requests / minute per user."""
    rate = '10/minute'
    scope = 'generation'


def clean_generated_content(content):
    """
    Clean generated content by removing formatting instructions like "(Section header: ...)".
    This ensures the stored content doesn't include AI prompt artifacts.
    """
    import re
    if not content:
        return content
    
    # Convert to string if it's not already
    if isinstance(content, dict):
        # If it's a dict, try to get the 'content' field or convert to string
        if 'content' in content:
            content = content['content']
        else:
            content = str(content)
    elif not isinstance(content, str):
        content = str(content)
    
    # Remove "(Section header: ...)" text from all lines
    cleaned_content = re.sub(r'\(section header[^)]*\)', '', content, flags=re.IGNORECASE)
    
    # Remove lines that are just "(section header: ...)"
    lines = cleaned_content.split('\n')
    filtered_lines = []
    for line in lines:
        line_stripped = line.strip()
        # Skip lines that are just the section header instruction
        if not re.match(r'^\s*\(section header[^)]*\)\s*$', line_stripped, re.IGNORECASE):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines).strip()


class GeneratedContentView(generics.ListAPIView):
    serializer_class = GeneratedContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Disable pagination for this endpoint

    def get_queryset(self):
        queryset = GeneratedContent.objects.filter(user=self.request.user).order_by('-created_at')
        # Filter by favorites if requested
        favorites_only = self.request.query_params.get('favorites', '').lower() == 'true'
        if favorites_only:
            # Only filter by is_favorite if the field exists in the database
            try:
                queryset = queryset.filter(is_favorite=True)
            except Exception:
                # If is_favorite field doesn't exist, return empty queryset
                logger.warning("is_favorite field not found in database, returning empty queryset for favorites filter")
                return GeneratedContent.objects.none()
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list to return a direct array instead of paginated response.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            # Handle case where is_favorite column doesn't exist in database
            if 'is_favorite' in str(e) or 'column' in str(e).lower():
                logger.warning(f"Database column error (likely missing is_favorite field): {e}")
                logger.info("Attempting to fetch content without is_favorite field...")
                # Try to fetch without the is_favorite filter
                try:
                    queryset = GeneratedContent.objects.filter(user=request.user).order_by('-created_at')
                    # Exclude is_favorite from serializer if it causes issues
                    serializer = self.get_serializer(queryset, many=True)
                    # Manually set is_favorite to False for all items
                    data = serializer.data
                    for item in data:
                        item['is_favorite'] = False
                    return Response(data)
                except Exception as inner_e:
                    logger.error(f"Error fetching content even without is_favorite: {inner_e}", exc_info=True)
                    return Response({'error': 'Failed to fetch content. Please run migrations.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                logger.error(f"Unexpected error in GeneratedContentView.list: {e}", exc_info=True)
                return Response({'error': 'Failed to fetch content.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ToggleFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, content_id):
        """
        Toggle favorite status for a generated content item.
        """
        try:
            content = GeneratedContent.objects.get(id=content_id, user=request.user)
            
            # Check if is_favorite field exists in the database
            try:
                # Try to access the field to see if it exists
                current_favorite = getattr(content, 'is_favorite', False)
                content.is_favorite = not current_favorite
                content.save(update_fields=['is_favorite', 'updated_at'])
            except Exception as field_error:
                # Check if this is a database column error
                error_str = str(field_error).lower()
                if 'is_favorite' in error_str or 'column' in error_str or 'no such column' in error_str:
                    logger.error(f"is_favorite field not found in database: {field_error}")
                    return Response({
                        'error': 'Favorite feature is not available. Please run migrations: python manage.py migrate generators 0001_initial --fake && python manage.py migrate generators'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # Re-raise if it's a different error
                raise
            
            return Response({
                'id': content.id,
                'is_favorite': content.is_favorite,
                'message': 'Added to favorites' if content.is_favorite else 'Removed from favorites'
            }, status=status.HTTP_200_OK)
        except GeneratedContent.DoesNotExist:
            return Response({
                'error': 'Content not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error toggling favorite for content {content_id}: {e}", exc_info=True)
            error_message = str(e) if settings.DEBUG else 'Failed to update favorite status'
            return Response({
                'error': error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteContentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, content_id):
        """
        Delete a generated content item.
        """
        try:
            content = GeneratedContent.objects.get(id=content_id, user=request.user)
            content_title = content.title
            content.delete()
            
            logger.info(f"Content {content_id} deleted by user {request.user.id}")
            return Response({
                'message': f'Content "{content_title}" has been deleted successfully.',
                'id': content_id
            }, status=status.HTTP_200_OK)
        except GeneratedContent.DoesNotExist:
            return Response({
                'error': 'Content not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {e}", exc_info=True)
            error_message = str(e) if settings.DEBUG else 'Failed to delete content'
            return Response({
                'error': error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonStarterGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [GenerationRateThrottle]

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST'))
    def post(self, request):
        # Check if OpenRouter API key is configured
        if not getattr(settings, 'OPENROUTER_API_KEY', ''):
            logger.error("OPENROUTER_API_KEY is not set")
            return Response({
                'error': 'AI service API key is not configured. Please contact support.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validate generation limit (membership tier check)
        try:
            validate_generation_limit(request.user)
        except serializers.ValidationError as e:
            logger.warning(f"Generation limit validation failed: {e}")
            error_message = str(e.detail[0]) if hasattr(e, 'detail') and e.detail else str(e)
            return Response({
                'error': error_message,
                'error_type': 'generation_limit_reached',
                'message': 'Your available generations have been used. Upgrade your plan to continue generating content.'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error during generation limit validation: {e}", exc_info=True)
            return Response({
                'error': 'Unable to validate generation limit. Please try again or contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = LessonStarterGenerateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Generate content using lesson starter via OpenRouter gateway
                try:
                    from .lesson_starter.logic import generate_lesson_starter_from_dict
                    from .lesson_starter.llm_client import OpenAILLMClient
                    
                    # Create LLM client backed by OpenRouter
                    llm_client = OpenAILLMClient(
                        generator_type='lesson_starter',
                        user_id=request.user.id,
                    )
                    
                    # Normalize grade level
                    grade = serializer.validated_data['grade_level'].capitalize()
                    if grade not in ('Elementary', 'Middle', 'High', 'College'):
                        grade = 'High'
                    
                    inputs_dict = {
                        'category': serializer.validated_data.get('subject', 'Science'),
                        'topic': serializer.validated_data['topic'],
                        'grade_level': grade,
                        'teacher_details': serializer.validated_data.get('customization', '')
                    }
                    
                    logger.info(f"Lesson starter inputs: {inputs_dict}")
                    
                    result = generate_lesson_starter_from_dict(
                        llm=llm_client,
                        inputs=inputs_dict,
                        max_attempts=1
                    )
                    
                    formatted_result = {
                        'content': result.get('output', '') or '',
                        'tokens_used': 0,
                        'generation_time': 0,
                    }
                    
                except PermissionError as e:
                    return Response({
                        'error': str(e),
                        'error_type': 'rate_limit',
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                except Exception as e:
                    logger.error(f"Lesson starter generation error: {e}", exc_info=True)
                    return Response({
                        'error': 'Failed to generate content with AI. Please try again.',
                        'detail': str(e) if settings.DEBUG else None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Validate result structure
                if not formatted_result or 'content' not in formatted_result:
                    logger.error(f"Invalid result structure from OpenAI: {formatted_result}")
                    return Response({
                        'error': 'Invalid response from AI service. Please try again.',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Clean content before saving - remove "(Section header: ...)" text
                cleaned_content = clean_generated_content(formatted_result.get('content', ''))
                
                # Save to database
                try:
                    generated_content = GeneratedContent.objects.create(
                        user=request.user,
                        content_type='lesson_starter',
                        title=f"Lesson Starter: {serializer.validated_data['topic']}",
                        content=cleaned_content,
                        input_parameters=serializer.validated_data,
                        tokens_used=formatted_result.get('tokens_used', 0),
                        generation_time=formatted_result.get('generation_time', 0)
                    )
                except Exception as e:
                    logger.error(f"Database error saving generated content: {e}", exc_info=True)
                    return Response({
                        'error': 'Failed to save generated content. Please try again.',
                        'detail': str(e) if settings.DEBUG else None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Increment generation count (non-blocking)
                try:
                    GenerationLimitService.increment_generation_count(request.user)
                except Exception as e:
                    logger.warning(f"Failed to increment generation count: {e}")
                    # Don't fail the request if counting fails
                
                # Build absolute URLs for downloads
                api_base_url = getattr(settings, 'API_BASE_URL', None)
                if not api_base_url:
                    # Fallback: construct from request
                    # Check X-Forwarded-Proto header (set by reverse proxy) or force HTTPS in production
                    forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO', '')
                    if forwarded_proto == 'https' or (not settings.DEBUG and 'api.foodsciencetoolbox.com' in request.get_host()):
                        scheme = 'https'
                    else:
                        scheme = 'https' if request.is_secure() else 'http'
                    host = request.get_host()
                    api_base_url = f"{scheme}://{host}"
                
                return Response({
                    'content': formatted_result.get('content', ''),
                    'formatted_docx_url': f'{api_base_url}/api/generators/{generated_content.id}/export/docx/',
                    'formatted_pdf_url': f'{api_base_url}/api/generators/{generated_content.id}/export/pdf/',
                    'tokens_used': formatted_result.get('tokens_used', 0),
                    'generation_time': formatted_result.get('generation_time', 0),
                    'id': generated_content.id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Unexpected error generating lesson starter: {e}", exc_info=True)
                return Response({
                    'error': 'Failed to generate content. Please try again or contact support.',
                    'detail': str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LearningObjectivesGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [GenerationRateThrottle]

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST'))
    def post(self, request):
        # Check if OpenRouter API key is configured
        if not getattr(settings, 'OPENROUTER_API_KEY', ''):
            logger.error("OPENROUTER_API_KEY is not set")
            return Response({
                'error': 'AI service API key is not configured. Please contact support.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validate generation limit
        try:
            validate_generation_limit(request.user)
        except serializers.ValidationError as e:
            # ValidationError contains the specific error message
            logger.warning(f"Generation limit validation failed: {e}")
            error_message = str(e.detail[0]) if hasattr(e, 'detail') and e.detail else str(e)
            return Response({
                'error': error_message,
                'error_type': 'generation_limit_reached',
                'message': 'Your available generations have been used. Upgrade your plan to continue generating content.'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error during generation limit validation: {e}", exc_info=True)
            return Response({
                'error': 'Unable to validate generation limit. Please try again or contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = LearningObjectivesGenerateSerializer(data=request.data)
        
        # Debug logging to see what data is being received
        logger.info(f"Learning objectives request data: {request.data}")
        
        if not serializer.is_valid():
            # Log the validation errors for debugging
            logger.error(f"Learning objectives serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate content using OpenAI service
            openai_service = OpenAIService()
            
            # Get validated data
            user_intent = serializer.validated_data.get('user_intent', 'Understand the topic')
            grade_level = serializer.validated_data['grade_level']
            num_objectives = serializer.validated_data['num_objectives']
            
            # Try new consolidated format first
            try:
                logger.info(f"Calling generate_learning_objectives with: user_intent={user_intent}, grade_level={grade_level}, num_objectives={num_objectives}")
                formatted_result = openai_service.generate_learning_objectives(
                    user_intent=user_intent,
                    grade_level=grade_level,
                    num_objectives=num_objectives
                )
                logger.info(f"OpenAI service returned: {formatted_result}")
            except Exception as e:
                logger.warning(f"Consolidated format failed, trying legacy: {e}")
                # Fallback to legacy format
                subject = serializer.validated_data.get('subject', 'Science')
                topic = serializer.validated_data.get('topic', 'Learning Objectives')
                customization = serializer.validated_data.get('customization', '')
                
                formatted_result = openai_service.generate_learning_objectives(
                    subject=subject,
                    grade_level=grade_level,
                    topic=topic,
                    number_of_objectives=num_objectives,
                    customization=customization
                )
            
            # Validate result structure
            if not formatted_result or 'content' not in formatted_result:
                logger.error(f"Invalid result structure from OpenAI: {formatted_result}")
                return Response({
                    'error': 'Invalid response from AI service. Please try again.',
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Clean content before saving
            cleaned_content = clean_generated_content(formatted_result.get('content', ''))
            
            # Save to database
            try:
                generated_content = GeneratedContent.objects.create(
                    user=request.user,
                    content_type='learning_objectives',
                    title=f"Learning Objectives: {serializer.validated_data.get('topic', 'Topic')}",
                    content=cleaned_content,
                    input_parameters=serializer.validated_data,
                    tokens_used=formatted_result.get('tokens_used', 0),
                    generation_time=formatted_result.get('generation_time', 0)
                )
            except Exception as e:
                logger.error(f"Database error saving generated content: {e}", exc_info=True)
                return Response({
                    'error': 'Failed to save generated content. Please try again.',
                    'detail': str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Increment generation count (non-blocking)
            try:
                GenerationLimitService.increment_generation_count(request.user)
            except Exception as e:
                logger.warning(f"Failed to increment generation count: {e}")
                # Don't fail the request if counting fails
            
            # Build absolute URLs for downloads
            api_base_url = getattr(settings, 'API_BASE_URL', None)
            if not api_base_url:
                # Fallback: construct from request
                # Check X-Forwarded-Proto header (set by reverse proxy) or force HTTPS in production
                forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO', '')
                if forwarded_proto == 'https' or (not settings.DEBUG and 'api.foodsciencetoolbox.com' in request.get_host()):
                    scheme = 'https'
                else:
                    scheme = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                api_base_url = f"{scheme}://{host}"
            
            return Response({
                'content': formatted_result['content'],
                'formatted_docx_url': f'{api_base_url}/api/generators/{generated_content.id}/export/docx/',
                'formatted_pdf_url': f'{api_base_url}/api/generators/{generated_content.id}/export/pdf/',
                'tokens_used': formatted_result.get('tokens_used', 0),
                'generation_time': formatted_result.get('generation_time', 0),
                'id': generated_content.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Unexpected error generating learning objectives: {e}", exc_info=True)
            return Response({
                'error': 'Failed to generate content. Please try again or contact support.',
                'detail': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiscussionQuestionsGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [GenerationRateThrottle]

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST'))
    def post(self, request):
        # Check if OpenRouter API key is configured
        if not getattr(settings, 'OPENROUTER_API_KEY', ''):
            logger.error("OPENROUTER_API_KEY is not set")
            return Response({
                'error': 'AI service API key is not configured. Please contact support.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validate generation limit (membership tier check)
        try:
            validate_generation_limit(request.user)
        except serializers.ValidationError as e:
            logger.warning(f"Generation limit validation failed: {e}")
            error_message = str(e.detail[0]) if hasattr(e, 'detail') and e.detail else str(e)
            return Response({
                'error': error_message,
                'error_type': 'generation_limit_reached',
                'message': 'Your available generations have been used. Upgrade your plan to continue generating content.'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error during generation limit validation: {e}", exc_info=True)
            return Response({
                'error': 'Unable to validate generation limit. Please try again or contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = DiscussionQuestionsGenerateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Generate content using discussion questions via OpenRouter
                try:
                    from .discussion_questions.logic import generate_discussion_questions_from_dict
                    from .discussion_questions.llm_client import OpenAILLMClient
                    
                    # Create LLM client backed by OpenRouter
                    llm_client = OpenAILLMClient(
                        generator_type='discussion_questions',
                        user_id=request.user.id,
                    )
                    
                    # Normalize grade level
                    raw_grade = serializer.validated_data['grade_level']
                    grade = raw_grade.lower().capitalize()
                    if grade not in ('Elementary', 'Middle', 'High', 'College'):
                        grade = 'High'
                    
                    inputs = {
                        'category': serializer.validated_data.get('subject', 'Food Science'),
                        'topic': serializer.validated_data['topic'],
                        'grade_level': grade,
                        'num_questions': 5,  # Always 5 questions
                        'teacher_details': serializer.validated_data.get('customization', '')
                    }
                    
                    logger.info(f"Discussion questions inputs: {inputs}")
                    
                    result = generate_discussion_questions_from_dict(
                        llm_client=llm_client,
                        inputs=inputs,
                        max_attempts=3
                    )
                    
                    formatted_result = {
                        'content': result.get('output', ''),
                        'tokens_used': 0,
                        'generation_time': 0,
                    }
                    
                except PermissionError as e:
                    return Response({
                        'error': str(e),
                        'error_type': 'rate_limit',
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                except Exception as e:
                    logger.error(f"Discussion questions generation error: {e}", exc_info=True)
                    return Response({
                        'error': 'Failed to generate content with AI. Please try again.',
                        'detail': str(e) if settings.DEBUG else None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Validate result structure
                if not formatted_result or 'content' not in formatted_result:
                    logger.error(f"Invalid result structure from OpenAI: {formatted_result}")
                    return Response({
                        'error': 'Invalid response from AI service. Please try again.',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Clean content before saving
                cleaned_content = clean_generated_content(formatted_result.get('content', ''))
                
                # Save to database
                try:
                    generated_content = GeneratedContent.objects.create(
                        user=request.user,
                        content_type='discussion_questions',
                        title=f"Discussion Questions: {serializer.validated_data['topic']}",
                        content=cleaned_content,
                        input_parameters=serializer.validated_data,
                        tokens_used=formatted_result.get('tokens_used', 0),
                        generation_time=formatted_result.get('generation_time', 0)
                    )
                except Exception as e:
                    logger.error(f"Database error saving generated content: {e}", exc_info=True)
                    return Response({
                        'error': 'Failed to save generated content. Please try again.',
                        'detail': str(e) if settings.DEBUG else None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Increment generation count (non-blocking)
                try:
                    GenerationLimitService.increment_generation_count(request.user)
                except Exception as e:
                    logger.warning(f"Failed to increment generation count: {e}")
                
                # Build absolute URLs for downloads
                api_base_url = getattr(settings, 'API_BASE_URL', None)
                if not api_base_url:
                    # Fallback: construct from request
                    # Check X-Forwarded-Proto header (set by reverse proxy) or force HTTPS in production
                    forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO', '')
                    if forwarded_proto == 'https' or (not settings.DEBUG and 'api.foodsciencetoolbox.com' in request.get_host()):
                        scheme = 'https'
                    else:
                        scheme = 'https' if request.is_secure() else 'http'
                    host = request.get_host()
                    api_base_url = f"{scheme}://{host}"
                
                return Response({
                    'content': formatted_result.get('content', ''),
                    'formatted_docx_url': f'{api_base_url}/api/generators/{generated_content.id}/export/docx/',
                    'formatted_pdf_url': f'{api_base_url}/api/generators/{generated_content.id}/export/pdf/',
                    'tokens_used': formatted_result.get('tokens_used', 0),
                    'generation_time': formatted_result.get('generation_time', 0),
                    'id': generated_content.id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Unexpected error generating discussion questions: {e}", exc_info=True)
                return Response({
                    'error': 'Failed to generate content. Please try again or contact support.',
                    'detail': str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [GenerationRateThrottle]

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST'))
    def post(self, request):
        # Check if OpenRouter API key is configured
        if not getattr(settings, 'OPENROUTER_API_KEY', ''):
            logger.error("OPENROUTER_API_KEY is not set")
            return Response({
                'error': 'AI service API key is not configured. Please contact support.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validate generation limit (membership tier check)
        try:
            validate_generation_limit(request.user)
        except serializers.ValidationError as e:
            logger.warning(f"Generation limit validation failed: {e}")
            error_message = str(e.detail[0]) if hasattr(e, 'detail') and e.detail else str(e)
            return Response({
                'error': error_message,
                'error_type': 'generation_limit_reached',
                'message': 'Your available generations have been used. Upgrade your plan to continue generating content.'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error during generation limit validation: {e}", exc_info=True)
            return Response({
                'error': 'Unable to validate generation limit. Please try again or contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = QuizGenerateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get user preferences for tone (with fallback)
                try:
                    tone = request.user.preferences.preferred_tone
                except (AttributeError, Exception):
                    tone = 'professional'
                
                # Generate quiz content via OpenRouter gateway
                try:
                    from .prompt_templates import QUIZ_TEMPLATE
                    prompt = QUIZ_TEMPLATE.format(
                        subject=serializer.validated_data['subject'],
                        grade_level=serializer.validated_data['grade_level'],
                        topic=serializer.validated_data['topic'],
                        number_of_questions=serializer.validated_data['number_of_questions'],
                        question_types=", ".join(serializer.validated_data['question_types']),
                        tone=tone
                    )
                    content_text = generate_ai_content(
                        generator_type='quiz',
                        prompt=prompt,
                        user_id=request.user.id,
                    )
                    result = {
                        'content': content_text,
                        'tokens_used': 0,
                        'generation_time': 0,
                    }
                except PermissionError as e:
                    return Response({
                        'error': str(e),
                        'error_type': 'rate_limit',
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                except Exception as e:
                    logger.error(f"Quiz generation error: {e}", exc_info=True)
                    return Response({
                        'error': 'Failed to generate content with AI. Please try again.',
                        'detail': str(e) if settings.DEBUG else None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Validate result structure
                if not result or 'content' not in result:
                    logger.error(f"Invalid result structure from OpenAI: {result}")
                    return Response({
                        'error': 'Invalid response from AI service. Please try again.',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Clean content before saving
                cleaned_content = clean_generated_content(result.get('content', ''))
                
                # Save to database
                try:
                    generated_content = GeneratedContent.objects.create(
                        user=request.user,
                        content_type='quiz',
                        title=f"Quiz: {serializer.validated_data['topic']}",
                        content=cleaned_content,
                        input_parameters=serializer.validated_data,
                        tokens_used=result.get('tokens_used', 0),
                        generation_time=result.get('generation_time', 0)
                    )
                except Exception as e:
                    logger.error(f"Database error saving generated content: {e}", exc_info=True)
                    return Response({
                        'error': 'Failed to save generated content. Please try again.',
                        'detail': str(e) if settings.DEBUG else None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Increment generation count (non-blocking)
                try:
                    GenerationLimitService.increment_generation_count(request.user)
                except Exception as e:
                    logger.warning(f"Failed to increment generation count: {e}")
                    # Don't fail the request if counting fails
                
                return Response({
                    'content': result['content'],
                    'tokens_used': result['tokens_used'],
                    'generation_time': result['generation_time'],
                    'id': generated_content.id
                }, status=status.HTTP_201_CREATED)
            except ValueError as e:
                logger.error(f"Error generating quiz: {e}")
                return Response({
                    'error': str(e),
                    'detail': 'Please check your OpenAI API key configuration.' if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"Unexpected error generating quiz: {e}", exc_info=True)
                return Response({
                    'error': 'Failed to generate content. Please try again or contact support.',
                    'detail': str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentExportView(APIView):
    """
    Export generated content as DOCX or PDF.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, content_id, format_type):
        """
        Export generated content.
        format_type: 'docx' or 'pdf'
        """
        try:
            generated_content = GeneratedContent.objects.get(
                id=content_id,
                user=request.user
            )
        except GeneratedContent.DoesNotExist:
            return Response(
                {'error': 'Content not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        formatter = DocumentFormatter()
        
        # Format based on content type
        if generated_content.content_type == 'discussion_questions' or generated_content.content_type == 'bell_ringer':
            topic = generated_content.input_parameters.get('topic', 'Topic')
            grade_level = generated_content.input_parameters.get('grade_level', 'High School')
            subject = generated_content.input_parameters.get('subject', 'Food Science')
            formatted_doc = formatter.format_discussion_questions(
                topic=topic,
                grade_level=grade_level,
                content=generated_content.content,
                subject=subject
            )
        elif generated_content.content_type == 'lesson_starter':
            topic = generated_content.input_parameters.get('topic', 'Topic')
            grade_level = generated_content.input_parameters.get('grade_level', 'High School')
            subject = generated_content.input_parameters.get('subject', 'Food Science')
            formatted_doc = formatter.format_lesson_starter(
                topic=topic,
                grade_level=grade_level,
                content=generated_content.content,
                subject=subject
            )
        elif generated_content.content_type == 'learning_objectives':
            topic = generated_content.input_parameters.get('user_intent', '') or generated_content.input_parameters.get('topic', 'Topic')
            grade_level = generated_content.input_parameters.get('grade_level', 'High School')
            subject = generated_content.input_parameters.get('subject', 'Food Science')
            formatted_doc = formatter.format_learning_objectives(
                topic=topic,
                grade_level=grade_level,
                content=generated_content.content,
                subject=subject
            )
        else:
            return Response(
                {'error': 'Export not supported for this content type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if format_type == 'docx':
            docx_buffer = formatted_doc['docx']
            # Ensure buffer is at the beginning
            docx_buffer.seek(0)
            # Read the entire buffer
            docx_data = docx_buffer.read()
            
            # Verify we have actual DOCX data (DOCX files start with PK\x03\x04)
            if len(docx_data) < 4 or not docx_data.startswith(b'PK\x03\x04'):
                logger.error(f"Invalid DOCX data generated. Buffer size: {len(docx_data)}")
                return Response(
                    {'error': 'Failed to generate DOCX file. Please try again.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Generate filename with proper extension
            filename = f"{generated_content.content_type}_{generated_content.id}.docx"
            # Use RFC 5987 encoding for filename to ensure proper handling
            from urllib.parse import quote
            encoded_filename = quote(filename)
            
            response = HttpResponse(
                docx_data,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            # Set Content-Disposition with both ASCII and UTF-8 encoded filename
            response['Content-Disposition'] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
            response['Content-Length'] = str(len(docx_data))
            return response
        
        elif format_type == 'pdf':
            # Generate actual PDF by converting DOCX to PDF
            try:
                docx_buffer = formatted_doc['docx']
                # Ensure DOCX buffer is at the beginning before conversion
                docx_buffer.seek(0)
                pdf_buffer = formatter.convert_docx_to_pdf(docx_buffer)
                # Ensure PDF buffer is at the beginning
                pdf_buffer.seek(0)
                # Read the entire PDF buffer
                pdf_data = pdf_buffer.read()
                
                # Verify we have actual PDF data (PDF files start with %PDF)
                if len(pdf_data) < 4 or not pdf_data.startswith(b'%PDF'):
                    logger.error(f"Invalid PDF data generated. Buffer size: {len(pdf_data)}")
                    return Response(
                        {'error': 'Failed to generate PDF file. Please try downloading as DOCX instead.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Generate filename with proper extension
                filename = f"{generated_content.content_type}_{generated_content.id}.pdf"
                from urllib.parse import quote
                encoded_filename = quote(filename)
                
                response = HttpResponse(
                    pdf_data,
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
                response['Content-Length'] = str(len(pdf_data))
                return response
            except ImportError as e:
                logger.error(f"PDF library not available: {e}")
                return Response(
                    {'error': 'PDF generation is not available. Please download as DOCX instead.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            except Exception as e:
                logger.error(f"Error generating PDF: {e}", exc_info=True)
                return Response(
                    {'error': 'Failed to generate PDF. Please try downloading as DOCX instead.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {'error': 'Invalid format. Use docx or pdf'},
            status=status.HTTP_400_BAD_REQUEST
        )