from rest_framework import serializers
from .models import MembershipTier, UserMembership


class MembershipTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipTier
        fields = (
            'id',
            'name',
            'display_name',
            'description',
            'monthly_price',
            'generation_limit',
            'is_active',
            'features',
            'created_at',
            'updated_at'
        )


class UserMembershipSerializer(serializers.ModelSerializer):
    tier = MembershipTierSerializer(read_only=True)
    remaining_generations = serializers.ReadOnlyField()
    
    class Meta:
        model = UserMembership
        fields = (
            'id',
            'tier',
            'generations_used_this_month',
            'remaining_generations',
            'status',
            'current_period_start',
            'current_period_end',
            'billing_interval',
            'created_at',
            'updated_at'
        )


class MembershipUpgradeSerializer(serializers.Serializer):
    tier_id = serializers.IntegerField()