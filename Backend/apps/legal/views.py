from rest_framework import generics, permissions
from .models import LegalDocument
from .serializers import LegalDocumentSerializer


class LegalDocumentListView(generics.ListAPIView):
    queryset = LegalDocument.objects.filter(is_active=True).order_by('-published_at')
    serializer_class = LegalDocumentSerializer
    permission_classes = [permissions.AllowAny]


class LegalDocumentDetailView(generics.RetrieveAPIView):
    queryset = LegalDocument.objects.filter(is_active=True)
    serializer_class = LegalDocumentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'document_type'


class LegalDocumentByTypeView(generics.RetrieveAPIView):
    serializer_class = LegalDocumentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'document_type'

    def get_queryset(self):
        return LegalDocument.objects.filter(is_active=True)
