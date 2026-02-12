from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, TeacherProfile, UserPreferences


class UserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'email_verified')
        read_only_fields = ('id', 'date_joined', 'email_verified')
    
    def get_email_verified(self, obj):
        """Get email verification status from teacher profile."""
        try:
            return obj.teacher_profile.email_verified
        except TeacherProfile.DoesNotExist:
            return False


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = (
            'is_academy_member',
            'email_verified',
            'terms_accepted',
            'terms_accepted_at',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = (
            'preferred_grade_level',
            'preferred_subject',
            'preferred_tone',
            'default_question_count',
            'updated_at'
        )
        read_only_fields = ('updated_at',)


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)
    last_name = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate_email(self, value):
        """Normalize and validate email."""
        if not value or not value.strip():
            raise serializers.ValidationError("Email is required.")
        email = value.strip().lower()
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email
    
    def validate_first_name(self, value):
        """Validate first name."""
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        return value.strip()

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs