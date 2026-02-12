"""
URL Configuration for Learning Objectives Endpoints
"""

from django.urls import path
from . import views

app_name = 'learning_objectives'

urlpatterns = [
    # Streaming endpoint (recommended for resilience)
    path('generate/', views.generate_learning_objectives_view, name='generate'),
    
    # Background job endpoints (alternative approach)
    path('jobs/submit/', views.submit_learning_objectives_job, name='submit_job'),
    path('jobs/<str:job_id>/status/', views.get_learning_objectives_job_status, name='job_status'),
    
    # DOCX export endpoint
    path('export/docx/', views.export_learning_objectives_docx, name='export_docx'),
]
