from django.urls import path
from .views import (
    LegalDocumentListView,
    LegalDocumentDetailView,
    LegalDocumentByTypeView
)

app_name = 'legal'

urlpatterns = [
    path('documents/', LegalDocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', LegalDocumentDetailView.as_view(), name='document-detail'),
    path('documents/type/<str:document_type>/', LegalDocumentByTypeView.as_view(), name='document-by-type'),
]