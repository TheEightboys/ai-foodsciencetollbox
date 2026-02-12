from django.db import models
from django.utils.translation import gettext_lazy as _


class LegalDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('terms_of_service', 'Terms of Service'),
        ('privacy_policy', 'Privacy Policy'),
        ('cookie_policy', 'Cookie Policy'),
        ('acceptable_use', 'Acceptable Use Policy'),
        ('dmca', 'DMCA Policy'),
    ]

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    version = models.CharField(max_length=20, default='1.0')
    
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'legal_documents'
        verbose_name = _('legal document')
        verbose_name_plural = _('legal documents')
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.get_document_type_display()} (v{self.version})"