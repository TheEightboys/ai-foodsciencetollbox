from rest_framework import serializers
from apps.memberships.models import MembershipTier, UserMembership
from apps.payments.models import PaymentHistory
from apps.accounts.models import User


class MembershipTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipTier
        fields = '__all__'


class UserMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    tier_name = serializers.CharField(source='tier.display_name', read_only=True)
    
    class Meta:
        model = UserMembership
        fields = '__all__'
        read_only_fields = ('user_email', 'tier_name')


class PaymentHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = PaymentHistory
        fields = '__all__'
        read_only_fields = ('user_email',)


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False)
    tier_name = serializers.CharField(required=False, help_text="trial, starter, or pro")


class UserListSerializer(serializers.ModelSerializer):
    membership_tier = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'is_active', 'membership_tier', 'membership_status')
    
    def get_membership_tier(self, obj):
        try:
            return obj.membership.tier.display_name if hasattr(obj, 'membership') else None
        except:
            return None
    
    def get_membership_status(self, obj):
        try:
            return obj.membership.status if hasattr(obj, 'membership') else None
        except:
            return None