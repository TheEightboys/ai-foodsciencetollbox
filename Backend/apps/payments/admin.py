from django.contrib import admin
from django.utils.html import format_html
from .models import StripeCustomer, PaymentHistory


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    """Admin interface for Stripe Customers"""
    list_display = ('user_email', 'stripe_customer_id', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    """Admin interface for Payment History"""
    list_display = ('user_email', 'amount_display', 'currency', 'status_display', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__email', 'stripe_payment_intent_id', 'description')
    readonly_fields = ('created_at', 'updated_at', 'metadata_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'amount', 'currency', 'status', 'description')
        }),
        ('Stripe Details', {
            'fields': ('stripe_payment_intent_id', 'metadata_display')
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
    
    def amount_display(self, obj):
        """Display amount with currency"""
        return f"${obj.amount:.2f} {obj.currency.upper()}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'succeeded': 'green',
            'pending': 'orange',
            'failed': 'red',
            'refunded': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def metadata_display(self, obj):
        """Display metadata in a readable format"""
        if obj.metadata:
            return format_html('<pre>{}</pre>', str(obj.metadata))
        return '—'
    metadata_display.short_description = 'Metadata'