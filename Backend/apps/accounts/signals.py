from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import User, TeacherProfile, UserPreferences


@receiver(post_save, sender=User)
def create_user_profile_and_preferences(sender, instance, created, **kwargs):
    """
    Create a teacher profile, user preferences, and trial membership when a user is created.
    """
    if created:
        TeacherProfile.objects.create(user=instance)
        UserPreferences.objects.create(user=instance)
        
        # Create trial membership
        try:
            from apps.memberships.models import MembershipTier, UserMembership
            trial_tier = MembershipTier.objects.filter(name='trial').first()
            if trial_tier:
                UserMembership.objects.create(
                    user=instance,
                    tier=trial_tier,
                    status='trialing',
                    current_period_start=timezone.now().date(),
                    current_period_end=(timezone.now() + timedelta(days=7)).date()
                )
        except Exception:
            # If membership app is not available or tier doesn't exist, skip
            pass
        
        # Send welcome email (async via Celery if available, otherwise skip)
        # NOTE: On Render free plan, Celery runs in EAGER mode (synchronous).
        # We wrap this in a broad try/except to avoid blocking user creation
        # or the OAuth callback if email sending hangs or fails.
        try:
            from apps.notifications.tasks import send_welcome_email
            send_welcome_email.delay(instance.id)
        except Exception as e:
            # Email sending is optional, never fail user creation for it
            import logging
            logging.getLogger(__name__).warning(
                f"Welcome email could not be sent for {instance.email}: {e}"
            )


@receiver(post_save, sender=User)
def save_user_profile_and_preferences(sender, instance, **kwargs):
    """
    Save the teacher profile and user preferences when a user is saved.
    """
    if hasattr(instance, 'teacher_profile'):
        instance.teacher_profile.save()
    if hasattr(instance, 'preferences'):
        instance.preferences.save()