from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from .managers import CustomUserManager


class User(AbstractUser):
    """Custom User model with email as username."""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email


class TeacherProfile(models.Model):
    """Teacher profile with email verification and password reset."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    is_academy_member = models.BooleanField(default=False, help_text="Food Science Academy member")
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Password reset
    password_reset_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    
    # Terms acceptance
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_profiles'
        verbose_name = _('teacher profile')
        verbose_name_plural = _('teacher profiles')
    
    def __str__(self):
        return f"Profile: {self.user.email}"
    
    def generate_verification_token(self):
        """Generate unique email verification token."""
        self.email_verification_token = str(uuid.uuid4())
        self.email_verification_sent_at = timezone.now()
        self.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
        return self.email_verification_token
    
    def generate_password_reset_token(self):
        """Generate password reset token with 1-hour expiry."""
        self.password_reset_token = str(uuid.uuid4())
        self.password_reset_expires = timezone.now() + timezone.timedelta(hours=1)
        self.save(update_fields=['password_reset_token', 'password_reset_expires'])
        return self.password_reset_token
    
    def verify_email(self):
        """Mark email as verified."""
        self.email_verified = True
        self.email_verification_token = None
        self.save(update_fields=['email_verified', 'email_verification_token'])


class UserPreferences(models.Model):
    """User preferences for content generation."""
    GRADE_LEVEL_CHOICES = [
        ('middle_school', 'Middle School (6-8)'),
        ('high_school', 'High School (9-12)'),
        ('mixed', 'Mixed Grade Levels'),
    ]
    
    SUBJECT_CHOICES = [
        ('food_science', 'Food Science'),
        ('consumer_science', 'Consumer Science'),
        ('nutrition', 'Nutrition'),
        ('culinary', 'Culinary Arts'),
        ('home_economics', 'Home Economics'),
    ]
    
    TONE_CHOICES = [
        ('formal', 'Formal & Academic'),
        ('conversational', 'Conversational & Friendly'),
        ('balanced', 'Balanced'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    preferred_grade_level = models.CharField(
        max_length=50,
        choices=GRADE_LEVEL_CHOICES,
        default='high_school'
    )
    
    preferred_subject = models.CharField(
        max_length=100,
        choices=SUBJECT_CHOICES,
        default='food_science'
    )
    
    preferred_tone = models.CharField(
        max_length=50,
        choices=TONE_CHOICES,
        default='balanced'
    )
    
    default_question_count = models.IntegerField(default=5)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = _('user preferences')
        verbose_name_plural = _('user preferences')
    
    def __str__(self):
        return f"Preferences: {self.user.email}"
