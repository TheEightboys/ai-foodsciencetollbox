from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class GeneratedContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('lesson_starter', 'Lesson Starter'),
        ('learning_objectives', 'Learning Objectives'),
        ('quiz', 'Quiz'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_content')
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Metadata
    input_parameters = models.JSONField(default=dict, blank=True)
    tokens_used = models.IntegerField(default=0)
    generation_time = models.FloatField(help_text="Generation time in seconds", null=True, blank=True)
    is_favorite = models.BooleanField(default=False, help_text="Whether this content is marked as favorite")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'generated_contents'
        verbose_name = _('generated content')
        verbose_name_plural = _('generated contents')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.content_type}) - {self.user.email}"