"""
URL Configuration for Lesson Starter Endpoints
"""

from django.urls import path
from . import views

app_name = 'lesson_starter'

urlpatterns = [
    # Streaming endpoint (recommended for resilience)
    path('generate/', views.generate_lesson_starter_view, name='generate'),
    
    # Background job endpoints (alternative approach)
    path('jobs/submit/', views.submit_lesson_starter_job, name='submit_job'),
    path('jobs/<str:job_id>/status/', views.get_lesson_starter_job_status, name='job_status'),
    
    # DOCX export endpoint
    path('export/docx/', views.export_lesson_starter_docx, name='export_docx'),
]
