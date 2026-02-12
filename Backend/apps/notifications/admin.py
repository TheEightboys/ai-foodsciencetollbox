from django.contrib import admin
from django.utils.html import format_html
from .models import EmailTemplate, EmailLog


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin interface for Email Templates"""
    list_display = ('name', 'subject', 'updated_at')
    search_fields = ('name', 'subject', 'plain_text_content')
    readonly_fields = ('created_at', 'updated_at', 'content_preview')
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'subject')
        }),
        ('Content', {
            'fields': ('content_preview', 'plain_text_content', 'html_content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Show content preview"""
        preview = obj.plain_text_content[:300] + '...' if len(obj.plain_text_content) > 300 else obj.plain_text_content
        return format_html('<div style="max-height: 200px; overflow-y: auto; padding: 10px; background: #f5f5f5; border-radius: 4px;">{}</div>', preview)
    content_preview.short_description = 'Content Preview'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin interface for Email Logs"""
    list_display = ('recipient', 'subject', 'status_display', 'user_email', 'sent_at')
    list_filter = ('status', 'template', 'sent_at')
    search_fields = ('recipient', 'subject', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('sent_at', 'content_preview', 'error_display')
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Email Information', {
            'fields': ('user', 'template', 'recipient', 'subject')
        }),
        ('Content', {
            'fields': ('content_preview', 'plain_text_content', 'html_content'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'error_display')
        }),
        ('Timestamps', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email if obj.user else '—'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def status_display(self, obj):
        """Display status with color coding"""
        if obj.status == 'sent':
            return format_html('<span style="color: green; font-weight: bold;">✓ Sent</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Failed</span>')
    status_display.short_description = 'Status'
    
    def content_preview(self, obj):
        """Show content preview"""
        preview = obj.plain_text_content[:200] + '...' if len(obj.plain_text_content) > 200 else obj.plain_text_content
        return format_html('<div style="max-height: 150px; overflow-y: auto; padding: 10px; background: #f5f5f5; border-radius: 4px;">{}</div>', preview)
    content_preview.short_description = 'Content Preview'
    
    def error_display(self, obj):
        """Display error message if any"""
        if obj.error_message:
            return format_html('<div style="color: red; padding: 10px; background: #ffe6e6; border-radius: 4px;">{}</div>', obj.error_message)
        return '—'
    error_display.short_description = 'Error Message'