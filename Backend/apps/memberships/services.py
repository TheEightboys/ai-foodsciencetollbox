from django.utils import timezone
from .models import UserMembership


class GenerationLimitService:
    """
    Service to handle generation limits for users based on their membership tier.
    """
    
    @staticmethod
    def ensure_membership_exists(user):
        """
        Ensure user has a membership. Creates one if it doesn't exist.
        Returns the membership object.
        """
        from .models import MembershipTier
        from django.utils import timezone
        from datetime import timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Use select_related to ensure tier is loaded
            return UserMembership.objects.select_related('tier').get(user=user)
        except UserMembership.DoesNotExist:
            # If no membership exists, create a default trial membership
            try:
                trial_tier = MembershipTier.objects.filter(name='trial').first()
                if not trial_tier:
                    # If trial tier doesn't exist, get the first active tier
                    trial_tier = MembershipTier.objects.filter(is_active=True).first()
                
                if not trial_tier:
                    # If no tiers exist, create a default trial tier
                    # No tiers found, creating default trial tier
                    trial_tier = MembershipTier.objects.create(
                        name='trial',
                        display_name='7-Day Trial',
                        description='Free trial with limited generations',
                        monthly_price=0.00,
                        generation_limit=10,
                        is_active=True,
                        display_order=0,
                        features=['10 generations', 'Word Downloads']
                    )
                
                membership = UserMembership.objects.create(
                    user=user,
                    tier=trial_tier,
                    status='trialing',
                    current_period_start=timezone.now().date(),
                    current_period_end=None  # Trial has no renewal date
                )
                # Fetch again with select_related to ensure tier is loaded
                return UserMembership.objects.select_related('tier').get(id=membership.id)
            except Exception as e:
                logger.error(f"Error creating membership for user {user.id}: {e}", exc_info=True)
                raise
    
    @staticmethod
    def can_generate_content(user):
        """
        Check if a user can generate content based on their membership limits.
        Automatically creates a default trial membership if one doesn't exist.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            membership = GenerationLimitService.ensure_membership_exists(user)
            # Ensure tier is loaded - access it explicitly
            tier = membership.tier
            
            # Direct check instead of using property to avoid any caching issues
            if membership.admin_override_unlimited:
                return True
            
            if tier.generation_limit is None:  # Unlimited
                return True
            
            can_generate = membership.generations_used_this_month < tier.generation_limit
            
            return can_generate
        except Exception as e:
            logger.error(f"Error checking generation limit for user {user.id}: {e}", exc_info=True)
            # If there's an error, allow generation to prevent blocking users
            # This is a fail-open approach for system errors
            # System error during validation - fail open to avoid blocking users
            return True
    
    @staticmethod
    def increment_generation_count(user):
        """
        Increment the generation count for a user.
        Sends limit reached email if user hits their limit.
        Automatically creates a default trial membership if one doesn't exist.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            membership = GenerationLimitService.ensure_membership_exists(user)
            # Tier should already be loaded via select_related, but access it to be sure
            tier = membership.tier
            
            # Always increment - we've already validated that user can generate
            old_count = membership.generations_used_this_month
            membership.generations_used_this_month += 1
            membership.save(update_fields=['generations_used_this_month'])
            
            # Check for 90% usage threshold (only if tier has a limit)
            if tier.generation_limit is not None and tier.generation_limit > 0:
                usage_percentage = (membership.generations_used_this_month / tier.generation_limit) * 100
                old_usage_percentage = (old_count / tier.generation_limit) * 100 if old_count > 0 else 0
                
                # Check if user just crossed 90% threshold (was below 90%, now at or above 90%)
                if old_usage_percentage < 90 and usage_percentage >= 90:
                    # Send 90% usage email
                    try:
                        from apps.notifications.services import EmailService
                        from django.conf import settings
                        frontend_url = settings.FRONTEND_URL
                        upgrade_url = f"{frontend_url}/pricing"
                        EmailService.send_90_percent_usage_email(user, upgrade_url)
                    except Exception:
                        # Email sending is optional
                        pass
                
                # Check if user just hit their limit (was below, now at limit)
                if membership.generations_used_this_month == tier.generation_limit:
                    # Send limit reached email
                    try:
                        from apps.notifications.services import EmailService
                        EmailService.send_limit_reached_email(user)
                    except Exception:
                        # Email sending is optional
                        pass
            
            return True
        except Exception as e:
            logger.error(f"Error incrementing generation count for user {user.id}: {e}", exc_info=True)
            # Don't fail the generation if we can't increment the count
            # This is a non-critical operation
            return True
    
    @staticmethod
    def reset_monthly_usage():
        """
        Reset the monthly generation count for all users.
        Sends monthly reset email to Starter plan users.
        This should be called periodically via a Celery task.
        """
        today = timezone.now().date()
        memberships_to_reset = UserMembership.objects.filter(
            last_reset_date__lt=today.replace(day=1)
        ).select_related('user', 'tier')
        
        updated_count = 0
        for membership in memberships_to_reset:
            membership.generations_used_this_month = 0
            membership.last_reset_date = today
            membership.save(update_fields=['generations_used_this_month', 'last_reset_date'])
            updated_count += 1
            
            # Send monthly reset email to Starter plan users (those with limits)
            if membership.tier.generation_limit is not None:
                try:
                    from apps.notifications.services import EmailService
                    EmailService.send_monthly_reset_email(membership.user)
                except Exception:
                    # Email sending is optional
                    pass
        
        return updated_count