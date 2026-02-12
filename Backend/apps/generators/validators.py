from rest_framework import serializers
from apps.memberships.services import GenerationLimitService


def validate_generation_limit(user):
    """
    Validate that the user can generate content based on their membership tier.
    Automatically creates a membership if one doesn't exist.
    """
    from apps.memberships.services import GenerationLimitService
    from apps.memberships.models import UserMembership
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Ensure membership exists first
        membership = GenerationLimitService.ensure_membership_exists(user)
        
        # Force load tier to ensure it's available
        tier = membership.tier
        
        logger.info(f"Validating generation limit for user {user.id}: "
                   f"membership_id={membership.id}, "
                   f"tier={tier.name}, "
                   f"generations_used={membership.generations_used_this_month}, "
                   f"limit={tier.generation_limit}")
        
        # Check if user can generate using the property
        can_generate = membership.can_generate_content
        
        logger.info(f"User {user.id} can_generate_content result: {can_generate}")
        
        if not can_generate:
            # User has reached their limit
            if tier.generation_limit is not None:
                raise serializers.ValidationError(
                    f"You have reached your generation limit for this month ({membership.generations_used_this_month}/{tier.generation_limit}). "
                    "Please upgrade your membership to continue generating content."
                )
            else:
                raise serializers.ValidationError(
                    "Unable to generate content. Please contact support."
                )
    except serializers.ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Error validating generation limit for user {user.id}: {e}", exc_info=True)
        # If there's a system error, allow generation (fail open)
        # This prevents blocking users due to system errors
        logger.warning(f"Allowing generation for user {user.id} due to validation error: {e}")
        pass


def validate_grade_level(value):
    """
    Validate that the grade level is one of the accepted values.
    """
    valid_grade_levels = [
        'middle_school', 'high_school', 'mixed'
    ]
    if value not in valid_grade_levels:
        raise serializers.ValidationError(
            f"Invalid grade level. Must be one of: {', '.join(valid_grade_levels)}"
        )


def validate_subject(value):
    """
    Validate that the subject is one of the accepted values.
    """
    valid_subjects = [
        'food_science', 'consumer_science', 'nutrition', 'culinary', 'home_economics'
    ]
    if value not in valid_subjects:
        raise serializers.ValidationError(
            f"Invalid subject. Must be one of: {', '.join(valid_subjects)}"
        )