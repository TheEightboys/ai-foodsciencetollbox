from django.contrib import admin
from django.utils.html import format_html
from .models import LegalDocument


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """Admin interface for Legal Documents"""
    list_display = ('document_type', 'title', 'version', 'is_active_display', 'published_at', 'updated_at')
    list_filter = ('document_type', 'is_active', 'published_at', 'created_at')
    search_fields = ('title', 'content', 'document_type')
    readonly_fields = ('created_at', 'updated_at', 'content_preview')
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Document Information', {
            'fields': ('document_type', 'title', 'version')
        }),
        ('Content', {
            'fields': ('content_preview', 'content')
        }),
        ('Status', {
            'fields': ('is_active', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        """Display active status with color"""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_display.short_description = 'Status'
    
    def content_preview(self, obj):
        """Show content preview"""
        preview = obj.content[:500] + '...' if len(obj.content) > 500 else obj.content
        return format_html('<div style="max-height: 300px; overflow-y: auto; padding: 10px; background: #f5f5f5; border-radius: 4px; white-space: pre-wrap;">{}</div>', preview)
    content_preview.short_description = 'Content Preview'
    
    actions = ['activate_documents', 'deactivate_documents']
    
    def activate_documents(self, request, queryset):
        """Admin action to activate documents"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'Activated {count} document(s).')
    activate_documents.short_description = 'Activate selected documents'
    
    def deactivate_documents(self, request, queryset):
        """Admin action to deactivate documents"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {count} document(s).')
    deactivate_documents.short_description = 'Deactivate selected documents'