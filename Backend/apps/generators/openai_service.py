import time
import logging
from django.conf import settings
from .prompt_templates import (
    LESSON_STARTER_TEMPLATE,
    LEARNING_OBJECTIVES_TEMPLATE,
    DISCUSSION_QUESTIONS_TEMPLATE,
    QUIZ_TEMPLATE
)
from .openrouter_gateway import generate_ai_content
from .shared.llm_client import LLMClient, OpenRouterLLMClient, OpenAILLMClient
from .consolidated.generator import ConsolidatedGenerator, ConsolidatedInput, generate_consolidated_learning_objectives
from .discussion_questions.logic import (
    generate_discussion_questions_from_dict as generate_dq_from_dict,
    DiscussionQuestionsInput
)
from .lesson_starter.logic import (
    generate_lesson_starter as generate_ls,
    LessonStarterInputs,
    LessonStarterGenerator
)

logger = logging.getLogger(__name__)


def parse_customization_input(customization_text: str) -> dict:
    """
    Parse user customization input into structured constraints.
    
    Stage A: Interpret user input into structured constraints.
    Returns a dictionary with parsed constraints.
    """
    if not customization_text or not customization_text.strip():
        return {}
    
    constraints = {
        'primary_topic_focus': None,
        'context_setting': None,
        'level_complexity': None,
        'number_of_items': None,
        'tone_style': None,
        'inclusions': [],
        'exclusions': [],
        'formatting_preferences': None,
        'special_instructions': []
    }
    
    text_lower = customization_text.lower()
    
    # Extract number of items if mentioned
    import re
    number_match = re.search(r'\b(\d+)\s*(objectives?|questions?|items?)\b', text_lower)
    if number_match:
        constraints['number_of_items'] = int(number_match.group(1))
    
    # Extract tone/style preferences
    tone_keywords = {
        'formal': ['formal', 'professional', 'academic'],
        'casual': ['casual', 'conversational', 'friendly'],
        'technical': ['technical', 'detailed', 'scientific'],
        'simple': ['simple', 'easy', 'basic', 'beginner']
    }
    for tone, keywords in tone_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            constraints['tone_style'] = tone
            break
    
    # Extract inclusions/exclusions
    if 'include' in text_lower or 'must have' in text_lower:
        # Try to extract what should be included
        include_match = re.search(r'(?:include|must have)[\s:]+([^.]+)', text_lower)
        if include_match:
            constraints['inclusions'].append(include_match.group(1).strip())
    
    if 'exclude' in text_lower or 'avoid' in text_lower or 'don\'t' in text_lower or "don't" in text_lower:
        exclude_match = re.search(r'(?:exclude|avoid|don\'?t)[\s:]+([^.]+)', text_lower)
        if exclude_match:
            constraints['exclusions'].append(exclude_match.group(1).strip())
    
    # Store the full text as special instructions if it doesn't fit other categories
    if not any([constraints['number_of_items'], constraints['tone_style'], constraints['inclusions'], constraints['exclusions']]):
        constraints['special_instructions'].append(customization_text.strip())
    else:
        # Add any remaining context as special instructions
        constraints['special_instructions'].append(customization_text.strip())
    
    return constraints


def build_customization_section(constraints: dict) -> str:
    """
    Build the user customization section for the prompt.
    Places user constraints near the top with clear labeling.
    """
    if not constraints or not any(constraints.values()):
        return ""
    
    sections = []
    
    if constraints.get('number_of_items'):
        sections.append(f"• Generate exactly {constraints['number_of_items']} items (objectives/questions/etc.)")
    
    if constraints.get('tone_style'):
        sections.append(f"• Use a {constraints['tone_style']} tone and style")
    
    if constraints.get('inclusions'):
        for inclusion in constraints['inclusions']:
            sections.append(f"• MUST include: {inclusion}")
    
    if constraints.get('exclusions'):
        for exclusion in constraints['exclusions']:
            sections.append(f"• MUST NOT include: {exclusion}")
    
    if constraints.get('special_instructions'):
        for instruction in constraints['special_instructions']:
            sections.append(f"• IMPORTANT: {instruction}")
    
    if not sections:
        return ""
    
    return "\n\nUSER CUSTOMIZATION (MUST FOLLOW - HIGH PRIORITY):\n" + "\n".join(sections) + "\n\nThe output must explicitly reflect these constraints. These user requirements take priority over default behavior unless they conflict with system rules, safety, or generator-specific structural requirements."

class OpenAIService:
    """
    Service to handle AI content generation.
    Now delegates all LLM calls through the centralised OpenRouter gateway.
    Kept for backward compatibility — views may still instantiate it.
    """

    def __init__(self):
        # No longer needs an OpenAI API key — everything goes via OpenRouter
        if not getattr(settings, 'OPENROUTER_API_KEY', ''):
            logger.warning("OPENROUTER_API_KEY is not set — AI generation will fail")

    def generate_lesson_starter(self, subject, grade_level, topic, duration_minutes=5, tone="balanced", customization=None):
        """
        Generate 7 lesson starter ideas using the v2 format.
        Duration is always 5 minutes (parameter kept for backward compatibility).
        """
        start_time = time.time()
        
        try:
            llm_client = OpenRouterLLMClient(generator_type='lesson_starter')
            
            # Normalize grade level
            final_grade_level = grade_level.lower().capitalize()
            if final_grade_level not in ['Elementary', 'Middle', 'High', 'College']:
                final_grade_level = 'High'
            
            inputs = LessonStarterInputs(
                category=subject,
                topic=topic,
                grade_level=final_grade_level,
                teacher_details=customization,
            )
            result_text = generate_ls(
                llm=llm_client,
                inputs=inputs,
                max_attempts=1,
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            return {
                'content': result_text,
                'tokens_used': 0,
                'generation_time': generation_time,
            }
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in lesson starter generation: {e}", exc_info=True)
            raise ValueError(f"Failed to generate content: {str(e)}")

    def generate_learning_objectives(self, user_intent=None, grade_level=None, num_objectives=5, subject=None, topic=None, number_of_objectives=None, customization=None):
        """
        Generate learning objectives using the consolidated generator.
        
        Args:
            user_intent: Natural language description of learning goal (new format)
            grade_level: Elementary, Middle, High, or College
            num_objectives: Target number (4-10, default 5)
            subject: Subject (legacy format)
            topic: Topic (legacy format)
            number_of_objectives: Number of objectives (legacy format)
            customization: Customization instructions (legacy format)
        """
        start_time = time.time()
        
        try:
            # Create LLM client backed by OpenRouter gateway
            llm_client = OpenRouterLLMClient(generator_type='learning_objectives')
            
            # Handle legacy format if user_intent is not provided
            if not user_intent and (subject or topic):
                # Build user_intent from legacy fields
                if topic:
                    user_intent = f"Understand {topic}"
                elif subject:
                    user_intent = f"Understand {subject}"
                else:
                    user_intent = "Understand the topic"
                    
                if customization:
                    user_intent += f" with focus on {customization}"
            
            # Use legacy number_of_objectives if provided
            if number_of_objectives:
                num_objectives = min(max(number_of_objectives, 4), 10)  # Clamp to 4-10 range
            
            # Normalize grade level
            if grade_level:
                normalized_grade = grade_level.lower().capitalize()
                if normalized_grade not in ['Elementary', 'Middle', 'High', 'College']:
                    normalized_grade = 'High'  # Default fallback
                grade_level = normalized_grade
            
            logger.info(f"Calling generate_consolidated_learning_objectives with: user_intent={user_intent}, grade_level={grade_level}, num_objectives={num_objectives}")
            result = generate_consolidated_learning_objectives(
                llm_client=llm_client,
                user_intent=user_intent or "Understand the topic",
                grade_level=grade_level or "High",
                num_objectives=num_objectives,
                max_attempts=2
            )
            logger.info(f"Consolidated generator returned: {result}")
            
            # Check if generation succeeded
            if not result.get('success', False):
                errors = result.get('critical_errors', [])
                last_output = result.get('last_output', '')
                logger.warning(f"Consolidated generation failed. Errors: {errors}")
                # If we have a last_output from the LLM, return it even if it didn't
                # pass strict validation — better to show imperfect content than nothing
                if last_output and isinstance(last_output, str) and len(last_output.strip()) > 20:
                    logger.info("Returning last_output despite validation failure")
                    content = last_output.strip()
                else:
                    raise ValueError(
                        "Unable to generate learning objectives that meet quality standards. "
                        "Please try again or adjust your requirements."
                    )
            else:
                content = result.get('rendered_text', result.get('output', ''))
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            return {
                'content': content,
                'tokens_used': 0,
                'generation_time': generation_time
            }
            
        except Exception as e:
            logger.error(f"Error generating learning objectives: {e}", exc_info=True)
            raise ValueError(f"Failed to generate learning objectives: {str(e)}")

    def generate_discussion_questions(self, subject, grade_level, topic, number_of_questions=5, tone="balanced", customization=None):
        """
        Generate 5 discussion questions using the v2 "Option N" format
        with validation and auto-repair loop (up to 3 attempts).
        """
        start_time = time.time()
        
        try:
            from .discussion_questions.logic import DiscussionQuestionsGenerator, DiscussionQuestionsInput
            llm_client = OpenRouterLLMClient(generator_type='discussion_questions')
            
            # Normalize grade level
            normalized_grade_level = grade_level.lower().capitalize()
            if normalized_grade_level not in ['Elementary', 'Middle', 'High', 'College']:
                normalized_grade_level = 'High'
            
            inputs = DiscussionQuestionsInput(
                category=subject,
                topic=topic,
                grade_level=normalized_grade_level,
                num_questions=5,  # Always 5
                teacher_details=customization
            )
            
            generator = DiscussionQuestionsGenerator(llm_client, max_attempts=3)
            result = generator.generate(inputs)
            result_text = result['output']
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            return {
                'content': result_text,
                'tokens_used': 0,
                'generation_time': generation_time
            }
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in discussion questions generation: {e}", exc_info=True)
            raise ValueError(f"Failed to generate content: {str(e)}")

    def generate_quiz(self, subject, grade_level, topic, number_of_questions, question_types, tone="balanced"):
        """
        Generate a quiz.
        """
        start_time = time.time()
        
        try:
            prompt = QUIZ_TEMPLATE.format(
                subject=subject,
                grade_level=grade_level,
                topic=topic,
                number_of_questions=number_of_questions,
                question_types=", ".join(question_types),
                tone=tone
            )
            
            # Use centralized OpenRouter gateway
            content = generate_ai_content(
                generator_type='quiz',
                prompt=prompt,
                system_message='You are an expert educational quiz creator.',
                user_id=None
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            if not content:
                raise ValueError("AI generation returned an empty response")
            
            return {
                'content': content,
                'tokens_used': 0,
                'generation_time': generation_time
            }
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in quiz generation: {e}", exc_info=True)
            raise ValueError(f"Failed to generate content: {str(e)}")