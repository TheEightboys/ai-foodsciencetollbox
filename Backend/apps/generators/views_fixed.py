from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse, FileResponse
from django.conf import settings
from .models import GeneratedContent
from .serializers import (
    GeneratedContentSerializer,
    LessonStarterGenerateSerializer,
    LearningObjectivesGenerateSerializer,
    DiscussionQuestionsGenerateSerializer,
    QuizGenerateSerializer
)
from .openai_service import OpenAIService
from .document_formatter import DocumentFormatter
from .validators import validate_generation_limit
from apps.memberships.services import GenerationLimitService
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


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

    def post(self, request):
        # Check if OpenAI API key is configured
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set")
            return Response({
                'error': 'OpenAI API key is not configured. Please contact support.',
                'detail': 'OPENAI_API_KEY environment variable is missing.'
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
        
        serializer = LessonStarterGenerateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get user preferences for tone (with fallback)
                try:
                    tone = request.user.preferences.preferred_tone
                except (AttributeError, Exception):
                    # If preferences don't exist or any error, use default
                    tone = 'professional'
                
                # Generate content using simplified lesson starter implementation
                try:
                    from .lesson_starter.logic import generate_lesson_starter, LessonStarterInputs
                    from apps.generators.shared.llm_client import OpenAILLMClient
                    
                    # Create LLM client
                    llm_client = OpenAILLMClient()
                    
                    # Create inputs dataclass
                    inputs = LessonStarterInputs(
                        category=serializer.validated_data.get('subject', 'Science'),
                        topic=serializer.validated_data['topic'],
                        grade_level=serializer.validated_data['grade_level'].capitalize(),  # Normalize grade level
                        time_needed=f"{serializer.validated_data['duration_minutes']}–{serializer.validated_data['duration_minutes'] + 1} minutes",
                        teacher_details=serializer.validated_data.get('customization', '')
                    )
                    
                    # Generate using new implementation
                    result_text = generate_lesson_starter(
                        llm=llm_client,
                        inputs=inputs,
                        max_attempts=3
                    )
                    
                    # Convert to expected format for frontend compatibility
                    formatted_result = {
                        'content': result_text,
                        'tokens_used': 0,  # Not tracked in new implementation
                        'generation_time': 0,  # Not tracked in new implementation
                    }
                    
                except Exception as e:
                    logger.error(f"Lesson starter generation error: {e}", exc_info=True)
                    # Fallback to old OpenAI service if new implementation fails
                    try:
                        openai_service = OpenAIService()
                        formatted_result = openai_service.generate_lesson_starter(
                            subject=serializer.validated_data['subject'],
                            grade_level=serializer.validated_data['grade_level'],
                            topic=serializer.validated_data['topic'],
                            duration_minutes=serializer.validated_data['duration_minutes'],
                            tone=tone,
                            customization=serializer.validated_data.get('customization', '')
                        )
                    except Exception as fallback_e:
                        logger.error(f"Both new and fallback implementations failed: {fallback_e}")
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

    def post(self, request):
        # Check if OpenAI API key is configured
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set")
            return Response({
                'error': 'OpenAI API key is not configured. Please contact support.',
                'detail': 'OPENAI_API_KEY environment variable is missing.'
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
        if not serializer.is_valid():
            # Log the validation errors for debugging
            logger.error(f"Learning objectives serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get user preferences for tone (with fallback)
            try:
                tone = request.user.preferences.preferred_tone
            except (AttributeError, Exception):
                # If preferences don't exist or any error, use default
                tone = 'professional'
            
            # Generate content using new consolidated learning objectives implementation
            try:
                openai_service = OpenAIService()
                
                # Use new consolidated format - prioritize user_intent
                user_intent = serializer.validated_data.get('user_intent')
                grade_level = serializer.validated_data['grade_level']
                num_objectives = serializer.validated_data['num_objectives']
                
                # Call with new consolidated parameters
                formatted_result = openai_service.generate_learning_objectives(
                    user_intent=user_intent,
                    grade_level=grade_level,
                    num_objectives=num_objectives
                )
                
            except Exception as e:
                logger.error(f"Learning objectives generation error: {e}", exc_info=True)
                # Fallback to legacy approach if consolidated fails
                try:
                    # Try legacy format as fallback
                    subject = serializer.validated_data.get('subject', 'Science')
                    topic = serializer.validated_data.get('topic', 'Learning Objectives')
                    number_of_objectives_legacy = serializer.validated_data.get('number_of_objectives', num_objectives)
                    customization = serializer.validated_data.get('customization', '')
                    
                    formatted_result = openai_service.generate_learning_objectives(
                        subject=subject,
                        grade_level=grade_level,
                        topic=topic,
                        number_of_objectives=number_of_objectives_legacy,
                        customization=customization
                    )
                    
                    # Add fallback warning
                    if 'warnings' not in formatted_result:
                        formatted_result['warnings'] = []
                    formatted_result['warnings'].append('Used legacy format due to consolidated system issue')
                    
                except Exception as fallback_e:
                    logger.error(f"Both consolidated and legacy implementations failed: {fallback_e}")
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
                'tokens_used': formatted_result['tokens_used'],
                'generation_time': formatted_result['generation_time'],
                'id': generated_content.id
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.error(f"Error generating learning objectives: {e}")
            return Response({
                'error': str(e),
                'detail': 'Please check your OpenAI API key configuration.' if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error generating learning objectives: {e}", exc_info=True)
            return Response({
                'error': 'Failed to generate content. Please try again or contact support.',
                'detail': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiscussionQuestionsGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Check if OpenAI API key is configured
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set")
            return Response({
                'error': 'OpenAI API key is not configured. Please contact support.',
                'detail': 'OPENAI_API_KEY environment variable is missing.'
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
        
        serializer = DiscussionQuestionsGenerateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get user preferences for tone (with fallback)
                try:
                    tone = request.user.preferences.preferred_tone
                except (AttributeError, Exception):
                    tone = 'professional'
                
                # Generate content using new discussion questions implementation
                try:
                    from .discussion_questions.logic import generate_discussion_questions_from_dict
                    from apps.generators.shared.llm_client import OpenAILLMClient
                    
                    # Create LLM client
                    llm_client = OpenAILLMClient()
                    
                    # Prepare inputs for new implementation
                    inputs = {
                        'category': serializer.validated_data.get('subject', 'Science'),
                        'topic': serializer.validated_data['topic'],
                        'grade_level': serializer.validated_data['grade_level'].capitalize(),  # Normalize grade level
                        'num_questions': serializer.validated_data.get('number_of_questions', 3),
                        'teacher_details': serializer.validated_data.get('customization', '')
                    }
                    
                    # Generate using new implementation
                    result = generate_discussion_questions_from_dict(
                        llm_client=llm_client,
                        inputs=inputs,
                        max_attempts=3
                    )
                    
                    # Convert to expected format for frontend compatibility
                    formatted_result = {
                        'content': result.get('output', ''),
                        'tokens_used': 0,  # Not tracked in new implementation
                        'generation_time': 0,  # Not tracked in new implementation
                    }
                    
                except Exception as e:
                    logger.error(f"Discussion questions generation error: {e}", exc_info=True)
                    # Fallback to old OpenAI service if new implementation fails
                    try:
                        openai_service = OpenAIService()
                        formatted_result = openai_service.generate_discussion_questions(
                            subject=serializer.validated_data['subject'],
                            grade_level=serializer.validated_data['grade_level'],
                            topic=serializer.validated_data['topic'],
                            number_of_questions=serializer.validated_data.get('number_of_questions', 3),
                            tone=tone,
                            customization=serializer.validated_data.get('customization', '')
                        )
                    except Exception as fallback_e:
                        logger.error(f"Both new and fallback implementations failed: {fallback_e}")
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
                logger.error(f"Unexpected error generating discussion questions: {e}", exc_info=True)
                return Response({
                    'error': 'Failed to generate content. Please try again or contact support.',
                    'detail': str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Check if OpenAI API key is configured
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set")
            return Response({
                'error': 'OpenAI API key is not configured. Please contact support.',
                'detail': 'OPENAI_API_KEY environment variable is missing.'
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
        
        serializer = QuizGenerateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get user preferences for tone (with fallback)
                try:
                    tone = request.user.preferences.preferred_tone
                except (AttributeError, Exception):
                    # If preferences don't exist or any error, use default
                    tone = 'professional'
                
                # Generate content using OpenAI service
                openai_service = OpenAIService()
                formatted_result = openai_service.generate_quiz(
                    subject=serializer.validated_data['subject'],
                    grade_level=serializer.validated_data['grade_level'],
                    topic=serializer.validated_data['topic'],
                    number_of_questions=serializer.validated_data.get('number_of_questions', 5),
                    question_types=serializer.validated_data.get('question_types', ['multiple_choice']),
                    tone=tone
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
                        content_type='quiz',
                        title=f"Quiz: {serializer.validated_data['topic']}",
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
                logger.error(f"Unexpected error generating quiz: {e}", exc_info=True)
                return Response({
                    'error': 'Failed to generate content. Please try again or contact support.',
                    'detail': str(e) if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExportContentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, content_id, format_type):
        """
        Export generated content as DOCX or PDF.
        
        Args:
            content_id: ID of the generated content
            format_type: Either 'docx' or 'pdf'
        """
        try:
            # Get the content
            content = GeneratedContent.objects.get(id=content_id, user=request.user)
            
            # Format the document
            formatter = DocumentFormatter()
            
            if format_type == 'docx':
                docx_buffer = formatter.create_docx(content.content, content.title)
                response = HttpResponse(
                    docx_buffer.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                response['Content-Disposition'] = f'attachment; filename="{content.title}.docx"'
                return response
                
            elif format_type == 'pdf':
                pdf_buffer = formatter.create_pdf(content.content, content.title)
                response = HttpResponse(
                    pdf_buffer.getvalue(),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = f'attachment; filename="{content.title}.pdf"'
                return response
                
            else:
                return Response({
                    'error': 'Invalid format type. Must be docx or pdf.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except GeneratedContent.DoesNotExist:
            return Response({
                'error': 'Content not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error exporting content {content_id}: {e}", exc_info=True)
            return Response({
                'error': 'Failed to export content. Please try again.',
                'detail': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring.
    """
    permission_classes = []  # Allow unrestricted access
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'teachai-generators'
        }, status=status.HTTP_200_OK)
