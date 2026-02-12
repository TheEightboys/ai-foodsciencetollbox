from rest_framework import serializers
from .models import GeneratedContent


class GeneratedContentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_favorite = serializers.BooleanField(default=False, required=False)
    
    class Meta:
        model = GeneratedContent
        fields = (
            'id',
            'user_email',
            'content_type',
            'title',
            'content',
            'input_parameters',
            'tokens_used',
            'generation_time',
            'is_favorite',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'user_email',
            'tokens_used',
            'generation_time',
            'created_at',
            'updated_at'
        )
    
    def to_representation(self, instance):
        """Override to handle missing is_favorite field gracefully"""
        data = super().to_representation(instance)
        # If is_favorite field doesn't exist in the database, default to False
        try:
            # Try to get the field value
            if hasattr(instance, 'is_favorite'):
                data['is_favorite'] = instance.is_favorite
            else:
                data['is_favorite'] = False
        except Exception:
            # If there's any error accessing the field, default to False
            data['is_favorite'] = False
        return data


class LessonStarterGenerateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100)
    grade_level = serializers.CharField(max_length=50)
    topic = serializers.CharField(max_length=200)
    customization = serializers.CharField(required=False, allow_blank=True, max_length=1000, help_text="Optional customization instructions to tailor the output")


class LearningObjectivesGenerateSerializer(serializers.Serializer):
    # NEW CONSOLIDATED DESIGN: Single prompt with user_intent
    user_intent = serializers.CharField(
        max_length=1000, 
        required=False,  # Made optional to support legacy fields
        allow_blank=True,
        help_text="Natural language description of what you want students to learn"
    )
    grade_level = serializers.ChoiceField(
        choices=[
            ('Elementary', 'Elementary (K-5)'),
            ('Middle', 'Middle School (6-8)'),
            ('High', 'High School (9-12)'),
            ('College', 'College/University')
        ],
        required=True,
        help_text="Grade level for the learning objectives"
    )
    num_objectives = serializers.IntegerField(
        default=5, 
        min_value=4, 
        max_value=10,
        help_text="Number of objectives to generate (4-10)"
    )
    
    # LEGACY FIELDS: Accepted but ignored for backward compatibility
    subject = serializers.CharField(
        max_length=100, 
        required=False, 
        write_only=True,
        help_text="Legacy field: Use user_intent instead"
    )
    topic = serializers.CharField(
        max_length=200, 
        required=False, 
        write_only=True,
        help_text="Legacy field: Use user_intent instead"
    )
    number_of_objectives = serializers.IntegerField(
        default=3, 
        min_value=1, 
        max_value=10,
        required=False,
        write_only=True,
        help_text="Legacy field: Use num_objectives instead"
    )
    customization = serializers.CharField(
        required=False, 
        allow_blank=True, 
        max_length=1000, 
        write_only=True,
        help_text="Legacy field: Include in user_intent instead"
    )
    
    def validate_grade_level(self, value):
        """Normalize grade level format."""
        return value.capitalize()
    
    def validate(self, attrs):
        """
        Handle legacy vs new input formats.
        If legacy fields are provided, construct user_intent from them.
        """
        # If user_intent is not provided but legacy fields are, construct user_intent
        if not attrs.get('user_intent') and (attrs.get('topic') or attrs.get('customization') or attrs.get('subject')):
            topic = attrs.get('topic', '').strip()
            subject = attrs.get('subject', '').strip()
            customization = attrs.get('customization', '').strip()
            
            # Use topic if available, otherwise use subject
            if topic:
                user_intent = f"Understand {topic}"
            elif subject:
                user_intent = f"Understand {subject}"
            else:
                user_intent = "Understand the topic"
                
            if customization:
                user_intent += f" with focus on {customization}"
            attrs['user_intent'] = user_intent
        elif not attrs.get('user_intent'):
            # If neither user_intent nor legacy fields are provided, set a default
            attrs['user_intent'] = "Understand the topic"
        
        # Handle legacy number_of_objectives vs new num_objectives
        if attrs.get('number_of_objectives') and not attrs.get('num_objectives'):
            legacy_num = attrs['number_of_objectives']
            # Convert legacy range (1-10) to new range (4-6)
            if legacy_num < 4:
                attrs['num_objectives'] = 4
            elif legacy_num > 6:
                attrs['num_objectives'] = 6
            else:
                attrs['num_objectives'] = legacy_num
        
        # Ensure num_objectives is within valid range
        if not attrs.get('num_objectives'):
            attrs['num_objectives'] = 5
        
        return attrs


class DiscussionQuestionsGenerateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100, default='Food Science')
    grade_level = serializers.CharField(max_length=50)
    topic = serializers.CharField(max_length=500)
    customization = serializers.CharField(required=False, allow_blank=True, max_length=1000, help_text="Optional teacher details to incorporate into questions")


class QuizGenerateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100)
    grade_level = serializers.CharField(max_length=50)
    topic = serializers.CharField(max_length=200)
    number_of_questions = serializers.IntegerField(default=5)
    question_types = serializers.MultipleChoiceField(choices=[
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer')
    ])