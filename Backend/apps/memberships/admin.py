from django.contrib import admin
from django.utils.html import format_html
from .models import MembershipTier, UserMembership


@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    """Admin interface for Membership Tiers"""
    list_display = ('display_name', 'name', 'monthly_price', 'stripe_price_id_display', 'generation_limit_display', 'is_active', 'display_order', 'member_count')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'display_name', 'description', 'stripe_price_id')
    ordering = ('display_order',)
    readonly_fields = ('created_at', 'updated_at', 'member_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Pricing', {
            'fields': ('monthly_price', 'stripe_price_id'),
            'description': 'Stripe Price ID must start with "price_" and come from Stripe Dashboard. Example: price_1SeQc3PwNxCKLfDfdpzjcyiZ'
        }),
        ('Limits', {
            'fields': ('generation_limit',)
        }),
        ('Admin Controls', {
            'fields': ('is_active', 'display_order', 'features')
        }),
        ('Statistics', {
            'fields': ('member_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def generation_limit_display(self, obj):
        """Display generation limit in a readable format"""
        if obj.generation_limit is None:
            return format_html('<span style="color: green; font-weight: bold;">Unlimited</span>')
        return obj.generation_limit
    generation_limit_display.short_description = 'Generation Limit'
    
    def member_count(self, obj):
        """Count of users with this tier"""
        return obj.memberships.count()
    member_count.short_description = 'Active Members'
    
    def stripe_price_id_display(self, obj):
        """Display Stripe Price ID with status"""
        if obj.stripe_price_id:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ {}</span>',
                obj.stripe_price_id
            )
        return format_html('<span style="color: red;">✗ NOT CONFIGURED</span>')
    stripe_price_id_display.short_description = 'Stripe Price ID'
    stripe_price_id_display.admin_order_field = 'stripe_price_id'


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    """Admin interface for User Memberships with advanced controls"""
    list_display = ('user_email', 'tier', 'status', 'usage_display', 'remaining_display', 'current_period_end', 'admin_override')
    list_filter = ('tier', 'status', 'admin_override_unlimited', 'current_period_end', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at', 'usage_percentage', 'remaining_generations', 'last_reset_date')
    date_hierarchy = 'current_period_end'
    
    def get_queryset(self, request):
        """Override queryset to handle missing billing_interval field gracefully"""
        from django.db import connection
        
        qs = super().get_queryset(request).select_related('user', 'tier')
        
        # Check if billing_interval column exists in the database
        # If not, use only() to explicitly fetch fields we need (excluding billing_interval)
        try:
            with connection.cursor() as cursor:
                # Use the actual table name from the model's Meta
                table_name = UserMembership._meta.db_table
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name=%s AND column_name='billing_interval'
                """, [table_name])
                if not cursor.fetchone():
                    # Column doesn't exist, use only() to fetch specific fields
                    # This avoids the error when Django tries to query the missing column
                    qs = qs.only(
                        'id', 'user_id', 'tier_id', 'generations_used_this_month',
                        'last_reset_date', 'stripe_customer_id', 'stripe_subscription_id',
                        'status', 'current_period_start', 'current_period_end',
                        'admin_override_unlimited', 'admin_notes', 'created_at', 'updated_at'
                    )
        except Exception:
            # If check fails, try using only() anyway as a safety measure
            try:
                qs = qs.only(
                    'id', 'user_id', 'tier_id', 'generations_used_this_month',
                    'last_reset_date', 'stripe_customer_id', 'stripe_subscription_id',
                    'status', 'current_period_start', 'current_period_end',
                    'admin_override_unlimited', 'admin_notes', 'created_at', 'updated_at'
                )
            except Exception:
                # If only() also fails, return queryset as-is
                # The error will need to be fixed by running the migration
                pass
        
        return qs
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'tier')
        }),
        ('Subscription Details', {
            'fields': ('status', 'stripe_customer_id', 'stripe_subscription_id')
        }),
        ('Usage Tracking', {
            'fields': ('generations_used_this_month', 'remaining_generations', 'usage_percentage', 'last_reset_date')
        }),
        ('Billing Period', {
            'fields': ('current_period_start', 'current_period_end')
        }),
        ('Admin Controls', {
            'fields': ('admin_override_unlimited', 'admin_notes'),
            'description': 'Admin can override generation limits and add notes'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def usage_display(self, obj):
        """Display usage with color coding"""
        if obj.tier.generation_limit is None:
            return format_html('<span style="color: green;">Unlimited</span>')
        percentage = obj.usage_percentage
        color = 'green' if percentage < 50 else 'orange' if percentage < 80 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.generations_used_this_month,
            obj.tier.generation_limit,
            percentage
        )
    usage_display.short_description = 'Usage'
    
    def remaining_display(self, obj):
        """Display remaining generations"""
        remaining = obj.remaining_generations
        if remaining is None:
            return format_html('<span style="color: green; font-weight: bold;">Unlimited</span>')
        return remaining
    remaining_display.short_description = 'Remaining'
    
    def admin_override(self, obj):
        """Display admin override status"""
        if obj.admin_override_unlimited:
            return format_html('<span style="color: orange; font-weight: bold;">✓ Override Active</span>')
        return '—'
    admin_override.short_description = 'Admin Override'
    
    actions = ['reset_usage', 'grant_unlimited', 'revoke_unlimited']
    
    def reset_usage(self, request, queryset):
        """Admin action to reset usage for selected memberships"""
        count = 0
        for membership in queryset:
            membership.generations_used_this_month = 0
            membership.save(update_fields=['generations_used_this_month'])
            count += 1
        self.message_user(request, f'Reset usage for {count} membership(s).')
    reset_usage.short_description = 'Reset usage to 0'
    
    def grant_unlimited(self, request, queryset):
        """Admin action to grant unlimited access"""
        count = queryset.update(admin_override_unlimited=True)
        self.message_user(request, f'Granted unlimited access to {count} membership(s).')
    grant_unlimited.short_description = 'Grant unlimited access'
    
    def revoke_unlimited(self, request, queryset):
        """Admin action to revoke unlimited access"""
        count = queryset.update(admin_override_unlimited=False)
        self.message_user(request, f'Revoked unlimited access from {count} membership(s).')
    revoke_unlimited.short_description = 'Revoke unlimited access'