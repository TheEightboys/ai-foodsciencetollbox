from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class StripeCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stripe_customers'
        verbose_name = _('stripe customer')
        verbose_name_plural = _('stripe customers')

    def __str__(self):
        return f"{self.user.email} - {self.stripe_customer_id}"


class PaymentHistory(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_history')
    stripe_payment_intent_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    description = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_histories'
        verbose_name = _('payment history')
        verbose_name_plural = _('payment histories')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.status}"