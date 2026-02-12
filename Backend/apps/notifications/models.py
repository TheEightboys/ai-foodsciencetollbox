from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class EmailTemplate(models.Model):
    NAME_CHOICES = [
        ('welcome', 'Welcome Email'),
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
        ('upgrade_confirmation', 'Upgrade Confirmation'),
        ('limit_reached', 'Generation Limit Reached'),  # Legacy - kept for backward compatibility
        ('limit_reached_trial', 'Generation Limit Reached - Trial'),
        ('limit_reached_starter', 'Generation Limit Reached - Starter'),
        ('90_percent_usage', '90% Usage Notification'),
        ('monthly_reset', 'Monthly Usage Reset'),
        ('support_acknowledgment', 'Support Ticket Acknowledgment'),
    ]

    name = models.CharField(max_length=50, choices=NAME_CHOICES, unique=True)
    subject = models.CharField(max_length=200)
    plain_text_content = models.TextField()
    html_content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'email_templates'
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')

    def __str__(self):
        return self.get_name_display()


class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    recipient = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    
    # Content
    plain_text_content = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_logs'
        verbose_name = _('email log')
        verbose_name_plural = _('email logs')
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.recipient} - {self.subject}"


class FeatureNotificationRequest(models.Model):
    """Track users who want to be notified when a feature becomes available"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feature_notifications')
    feature_name = models.CharField(max_length=200)
    user_email = models.EmailField()
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'feature_notification_requests'
        verbose_name = _('feature notification request')
        verbose_name_plural = _('feature notification requests')
        ordering = ['-created_at']
        unique_together = ['user', 'feature_name']

    def __str__(self):
        return f"{self.user_email} - {self.feature_name}"
