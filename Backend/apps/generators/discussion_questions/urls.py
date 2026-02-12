"""
URL Configuration for Discussion Questions Endpoints
"""

from django.urls import path
from . import views

app_name = 'discussion_questions'

urlpatterns = [
    # Streaming endpoint (recommended for resilience)
    path('generate/', views.generate_discussion_questions_view, name='generate'),
    
    # Background job endpoints (alternative approach)
    path('jobs/submit/', views.submit_discussion_questions_job, name='submit_job'),
    path('jobs/<str:job_id>/status/', views.get_discussion_questions_job_status, name='job_status'),
    
    # DOCX export endpoint
    path('export/docx/', views.export_discussion_questions_docx, name='export_docx'),
]
