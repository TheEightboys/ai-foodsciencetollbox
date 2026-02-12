from celery import shared_task
from django.utils import timezone
from .services import GenerationLimitService
from .models import UserMembership


@shared_task
def reset_monthly_usage():
    """
    Celery task to reset monthly generation usage for all users.
    Should be scheduled to run on the first day of each month.
    """
    try:
        count = GenerationLimitService.reset_monthly_usage()
        return f"Successfully reset monthly usage for {count} users."
    except Exception as e:
        return f"Error resetting monthly usage: {str(e)}"


@shared_task
def check_subscription_status():
    """
    Celery task to check and update subscription statuses.
    Should be scheduled to run daily.
    """
    try:
        today = timezone.now().date()
        expired_subscriptions = UserMembership.objects.filter(
            current_period_end__lt=today,
            status='active'
        ).update(status='past_due')
        
        return f"Updated {expired_subscriptions} expired subscriptions to past_due status."
    except Exception as e:
        return f"Error checking subscription status: {str(e)}"