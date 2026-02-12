from rest_framework import serializers
from .models import PaymentHistory


class PaymentHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = PaymentHistory
        fields = (
            'id',
            'user_email',
            'stripe_payment_intent_id',
            'amount',
            'currency',
            'status',
            'description',
            'metadata',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'user_email',
            'stripe_payment_intent_id',
            'amount',
            'currency',
            'status',
            'created_at',
            'updated_at'
        )