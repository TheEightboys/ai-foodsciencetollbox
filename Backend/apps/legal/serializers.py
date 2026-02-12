from rest_framework import serializers
from .models import LegalDocument


class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')