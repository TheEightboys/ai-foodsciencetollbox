from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User

class MembershipTier(models.Model):
    TIER_CHOICES = [
        ('trial', '7-Day Trial'),
        ('starter', 'Starter'),
        ('pro', 'Pro'),
    ]
    
    name = models.CharField(max_length=50, choices=TIER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    monthly_price = models.DecimalField(max_digits=6, decimal_places=2)
    generation_limit = models.IntegerField(
        null=True, 
        blank=True,
        help_text="null = unlimited generations"
    )
    
    stripe_price_id = models.CharField(max_length=100, blank=True)
    
    # Admin controls
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    features = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'membership_tiers'
        ordering = ['display_order']
        verbose_name = _('membership tier')
        verbose_name_plural = _('membership tiers')
    
    def __str__(self):
        return self.display_name

class UserMembership(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('trialing', 'Trialing'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    tier = models.ForeignKey(MembershipTier, on_delete=models.PROTECT, related_name='memberships')
    
    # Usage tracking
    generations_used_this_month = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)
    
    # Subscription details
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    current_period_start = models.DateField(null=True, blank=True)
    current_period_end = models.DateField(null=True, blank=True)
    billing_interval = models.CharField(
        max_length=10,
        choices=[('month', 'Monthly'), ('year', 'Yearly')],
        null=True,
        blank=True,
        help_text="Billing interval: monthly or yearly subscription"
    )
    
    # Admin overrides
    admin_override_unlimited = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_memberships'
        verbose_name = _('user membership')
        verbose_name_plural = _('user memberships')
    
    def __str__(self):
        return f"{self.user.email} - {self.tier.display_name}"
    
    @property
    def can_generate_content(self):
        """Check if user can generate content based on their tier limits"""
        if self.admin_override_unlimited:
            return True
        
        if self.tier.generation_limit is None:  # Unlimited
            return True
            
        return self.generations_used_this_month < self.tier.generation_limit
    
    @property
    def remaining_generations(self):
        """Calculate remaining generations for the month"""
        if self.admin_override_unlimited:
            return None  # Unlimited
        
        if self.tier.generation_limit is None:  # Unlimited
            return None
            
        return max(0, self.tier.generation_limit - self.generations_used_this_month)
    
    @property
    def usage_percentage(self):
        """Calculate usage percentage (0-100)"""
        if self.admin_override_unlimited or self.tier.generation_limit is None:
            return 0
        if self.tier.generation_limit == 0:
            return 100
        return int((self.generations_used_this_month / self.tier.generation_limit) * 100)