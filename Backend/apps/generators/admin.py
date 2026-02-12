from django.contrib import admin
from django.utils.html import format_html
from .models import GeneratedContent


@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    """Admin interface for Generated Content"""
    list_display = ('title', 'content_type', 'user_email', 'tokens_used', 'generation_time_display', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('title', 'content', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'content_preview', 'input_parameters_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Content Information', {
            'fields': ('user', 'content_type', 'title')
        }),
        ('Content', {
            'fields': ('content_preview', 'content')
        }),
        ('Input Parameters', {
            'fields': ('input_parameters_display',),
            'classes': ('collapse',)
        }),
        ('Generation Metadata', {
            'fields': ('tokens_used', 'generation_time')
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
    
    def generation_time_display(self, obj):
        """Display generation time in readable format"""
        if obj.generation_time:
            if obj.generation_time < 1:
                return f"{obj.generation_time * 1000:.0f}ms"
            return f"{obj.generation_time:.2f}s"
        return '—'
    generation_time_display.short_description = 'Time'
    
    def content_preview(self, obj):
        """Show content preview"""
        preview = obj.content[:200] + '...' if len(obj.content) > 200 else obj.content
        return format_html('<div style="max-height: 200px; overflow-y: auto; padding: 10px; background: #f5f5f5; border-radius: 4px;">{}</div>', preview)
    content_preview.short_description = 'Content Preview'
    
    def input_parameters_display(self, obj):
        """Display input parameters in a readable format"""
        if obj.input_parameters:
            return format_html('<pre>{}</pre>', str(obj.input_parameters))
        return '—'
    input_parameters_display.short_description = 'Input Parameters'