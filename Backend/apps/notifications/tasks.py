from celery import shared_task
from django.contrib.auth import get_user_model
from .services import EmailService
from apps.memberships.models import UserMembership

User = get_user_model()


@shared_task
def send_welcome_email(user_id):
    """
    Celery task to send a welcome email to a new user.
    """
    try:
        user = User.objects.get(id=user_id)
        success = EmailService.send_welcome_email(user)
        return f"Welcome email sent to {user.email}: {'Success' if success else 'Failed'}"
    except User.DoesNotExist:
        return f"User with ID {user_id} does not exist"


@shared_task
def send_limit_reached_email(user_id):
    """
    Celery task to send a limit reached email to a user.
    """
    try:
        user = User.objects.get(id=user_id)
        success = EmailService.send_limit_reached_email(user)
        return f"Limit reached email sent to {user.email}: {'Success' if success else 'Failed'}"
    except User.DoesNotExist:
        return f"User with ID {user_id} does not exist"


@shared_task
def send_monthly_reset_email(user_id):
    """
    Celery task to send a monthly reset email to a user.
    """
    try:
        user = User.objects.get(id=user_id)
        success = EmailService.send_monthly_reset_email(user)
        return f"Monthly reset email sent to {user.email}: {'Success' if success else 'Failed'}"
    except User.DoesNotExist:
        return f"User with ID {user_id} does not exist"


@shared_task
def send_upgrade_confirmation_email(user_id, tier_name):
    """
    Celery task to send an upgrade confirmation email to a user.
    """
    try:
        user = User.objects.get(id=user_id)
        success = EmailService.send_upgrade_confirmation_email(user, tier_name)
        return f"Upgrade confirmation email sent to {user.email}: {'Success' if success else 'Failed'}"
    except User.DoesNotExist:
        return f"User with ID {user_id} does not exist"