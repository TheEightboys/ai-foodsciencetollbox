"""
Comprehensive Unit Tests for Consolidated Learning Objectives System
Tests all components of the new consolidated approach:
- Grade profiles with complexity descriptors
- Consolidated generator with domain routing
- Consolidated validator with critical/warning separation
- OpenAI service integration
- Backward compatibility
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from rest_framework import serializers

# Import consolidated components
from apps.generators.consolidated.grade_profiles import (
    GradeProfile, 
    get_grade_profile, 
    get_grade_verbs, 
    validate_grade_appropriateness,
    GRADE_PROFILES
)
from apps.generators.consolidated.generator import (
    ConsolidatedInput,
    ConsolidatedGenerator,
    generate_consolidated_learning_objectives
)
from apps.generators.consolidated.validator import (
    ValidationResult,
    ConsolidatedValidator,
    validate_consolidated_learning_objectives
)
from apps.generators.serializers import LearningObjectivesGenerateSerializer
from apps.generators.openai_service import OpenAIService, OpenAILLMClient


class TestGradeProfiles(TestCase):
    """Test grade profiles functionality."""
    
    def test_get_grade_profile_valid_levels(self):
        """Test getting valid grade profiles."""
        for grade_level in ['Elementary', 'Middle', 'High', 'College']:
            profile = get_grade_profile(grade_level)
            self.assertIsInstance(profile, GradeProfile)
            self.assertEqual(profile.name, grade_level)
    
    def test_get_grade_profile_invalid_level(self):
        """Test getting invalid grade profile defaults to High."""
        profile = get_grade_profile('Invalid')
        self.assertEqual(profile.name, 'High')
    
    def test_get_grade_verbs(self):
        """Test getting grade-appropriate verbs."""
        verbs = get_grade_verbs('Elementary')
        self.assertIn('expected', verbs)
        self.assertIn('forbidden', verbs)
        self.assertIn('Identify', verbs['expected'])
        self.assertIn('Analyze', verbs['forbidden'])
    
    def test_validate_grade_appropriateness(self):
        """Test grade appropriateness validation."""
        objectives = [
            "Identify the main parts of a plant.",
            "Describe the process of photosynthesis.",
            "Compare different types of rocks."
        ]
        
        result = validate_grade_appropriateness(objectives, 'Elementary')
        
        self.assertIn('appropriate_count', result)
        self.assertIn('total_count', result)
        self.assertIn('percentage', result)
        self.assertIn('issues', result)
        self.assertEqual(result['total_count'], 3)
    
    def test_grade_profile_completeness(self):
        """Test that all grade profiles have required fields."""
        required_fields = [
            'name', 'cognitive_level', 'independence_level',
            'expected_verbs', 'forbidden_verbs', 'complexity_guidance',
            'context_expectations', 'source_expectations', 'time_frame',
            'expected_products', 'teacher_support'
        ]
        
        for grade_level, profile in GRADE_PROFILES.items():
            for field in required_fields:
                self.assertTrue(hasattr(profile, field), 
                              f"Missing {field} in {grade_level} profile")


class TestConsolidatedInput(TestCase):
    """Test consolidated input model."""
    
    def test_valid_input(self):
        """Test valid consolidated input."""
        input_data = {
            'user_intent': 'Understand how bacteria multiply at different temperatures',
            'grade_level': 'Middle',
            'num_objectives': 5
        }
        
        serializer = LearningObjectivesGenerateSerializer(data=input_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user_intent'], 
                        input_data['user_intent'])
        self.assertEqual(serializer.validated_data['grade_level'], 
                        input_data['grade_level'])
        self.assertEqual(serializer.validated_data['num_objectives'], 
                        input_data['num_objectives'])
    
    def test_invalid_grade_level(self):
        """Test invalid grade level."""
        input_data = {
            'user_intent': 'Understand how bacteria multiply at different temperatures',
            'grade_level': 'Invalid',
            'num_objectives': 5
        }
        
        serializer = LearningObjectivesGenerateSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('grade_level', serializer.errors)
    
    def test_invalid_num_objectives(self):
        """Test invalid number of objectives."""
        input_data = {
            'user_intent': 'Understand how bacteria multiply at different temperatures',
            'grade_level': 'Middle',
            'num_objectives': 10  # Too many
        }
        
        serializer = LearningObjectivesGenerateSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('num_objectives', serializer.errors)
    
    def test_short_user_intent(self):
        """Test user intent that's too short."""
        input_data = {
            'user_intent': 'Too short',
            'grade_level': 'Middle',
            'num_objectives': 5
        }
        
        serializer = LearningObjectivesGenerateSerializer(data=input_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_intent', serializer.errors)
    
    def test_backward_compatibility_conversion(self):
        """Test legacy field conversion to user_intent."""
        input_data = {
            # Legacy fields
            'subject': 'Science',
            'topic': 'Bacteria',
            'number_of_objectives': 4,
            'customization': 'Focus on temperature effects',
            # New fields absent
        }
        
        serializer = LearningObjectivesGenerateSerializer(data=input_data)
        self.assertTrue(serializer.is_valid())
        
        # Should convert to user_intent
        expected_intent = "Understand Bacteria with focus on temperature effects"
        self.assertEqual(serializer.validated_data['user_intent'], expected_intent)
        self.assertEqual(serializer.validated_data['num_objectives'], 4)


class TestConsolidatedValidator(TestCase):
    """Test consolidated validator functionality."""
    
    def setUp(self):
        self.validator = ConsolidatedValidator()
    
    def test_valid_learning_objectives(self):
        """Test validation of valid learning objectives."""
        valid_output = """Lesson Objectives

Grade Level: Middle
Topic: Bacterial Growth

By the end of this lesson, students will be able to:
1. Explain how temperature affects bacterial growth rate.
2. Compare bacterial growth in different food storage conditions.
3. Calculate the doubling time of bacteria under optimal conditions.
4. Analyze factors that inhibit bacterial multiplication.
5. Design an experiment to test bacterial growth variables."""
        
        result = self.validator.validate(
            output=valid_output,
            grade_level='Middle',
            user_intent='Understand bacterial growth'
        )
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.critical_errors), 0)
        self.assertIsInstance(result.extracted_data, dict)
        self.assertEqual(len(result.extracted_data['objectives']), 5)
    
    def test_missing_structure_elements(self):
        """Test validation fails with missing structure."""
        invalid_output = """By the end of this lesson, students will be able to:
1. Explain how temperature affects bacterial growth rate.
2. Compare bacterial growth in different food storage conditions."""
        
        result = self.validator.validate(
            output=invalid_output,
            grade_level='Middle'
        )
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.critical_errors), 0)
        self.assertTrue(any('Grade Level:' in error for error in result.critical_errors))
    
    def test_forbidden_verbs(self):
        """Test validation catches forbidden verbs."""
        invalid_output = """Lesson Objectives

Grade Level: Middle
Topic: Bacterial Growth

By the end of this lesson, students will be able to:
1. Learn about bacterial growth.
2. Understand temperature effects.
3. Know the factors that influence multiplication."""
        
        result = self.validator.validate(
            output=invalid_output,
            grade_level='Middle'
        )
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.critical_errors), 0)
        self.assertTrue(any('Learn' in error for error in result.critical_errors))
    
    def test_grade_inappropriate_verbs(self):
        """Test validation catches grade-inappropriate verbs."""
        invalid_output = """Lesson Objectives

Grade Level: Elementary
Topic: Plant Growth

By the end of this lesson, students will be able to:
1. Analyze the process of photosynthesis.
2. Evaluate different soil types.
3. Critique plant growth conditions."""
        
        result = self.validator.validate(
            output=invalid_output,
            grade_level='Elementary'
        )
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.critical_errors), 0)
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        valid_output = """Lesson Objectives

Grade Level: High
Topic: Chemical Reactions

By the end of this lesson, students will be able to:
1. Analyze the factors that affect reaction rates.
2. Evaluate the efficiency of different catalysts.
3. Design an experiment to test reaction variables."""
        
        result = self.validator.validate(
            output=valid_output,
            grade_level='High'
        )
        
        self.assertIsInstance(result.quality_score, float)
        self.assertGreater(result.quality_score, 0.5)  # Should be reasonably high


class TestConsolidatedGenerator(TestCase):
    """Test consolidated generator functionality."""
    
    def setUp(self):
        # Mock LLM client
        self.mock_llm_client = Mock()
        self.mock_llm_client.generate_text.return_value = """Lesson Objectives

Grade Level: Middle
Topic: Bacterial Growth

By the end of this lesson, students will be able to:
1. Explain how temperature affects bacterial growth rate.
2. Compare bacterial growth in different food storage conditions.
3. Calculate the doubling time of bacteria under optimal conditions.
4. Analyze factors that inhibit bacterial multiplication.
5. Design an experiment to test bacterial growth variables."""
        
        self.generator = ConsolidatedGenerator(self.mock_llm_client)
    
    def test_successful_generation(self):
        """Test successful generation cycle."""
        inputs = ConsolidatedInput(
            user_intent='Understand how bacteria multiply at different temperatures',
            grade_level='Middle',
            num_objectives=5
        )
        
        with patch('apps.generators.consolidated.generator.route_to_domain') as mock_routing:
            mock_routing.return_value = {
                'domain': 'microbiology',
                'confidence': 0.9,
                'apply_food_overlay': True,
                'domain_description': 'Microbiology'
            }
            
            result = self.generator.generate(inputs)
            
            self.assertTrue(result['success'])
            self.assertEqual(len(result['objectives']), 5)
            self.assertIn('observability', result)
            self.assertIn('routing', result)
            self.assertIn('quality_metrics', result)
    
    def test_generation_with_validation_failure(self):
        """Test generation with validation failure and repair."""
        # First attempt fails, second succeeds
        self.mock_llm_client.generate_text.side_effect = [
            # First attempt - invalid output
            "Invalid output without proper structure",
            # Second attempt - valid output
            """Lesson Objectives

Grade Level: Middle
Topic: Bacterial Growth

By the end of this lesson, students will be able to:
1. Explain how temperature affects bacterial growth rate."""
        ]
        
        inputs = ConsolidatedInput(
            user_intent='Understand bacterial growth',
            grade_level='Middle',
            num_objectives=1  # Only need 1 for second attempt
        )
        
        with patch('apps.generators.consolidated.generator.route_to_domain') as mock_routing:
            mock_routing.return_value = {
                'domain': 'microbiology',
                'confidence': 0.9,
                'apply_food_overlay': False,
                'domain_description': 'Microbiology'
            }
            
            result = self.generator.generate(inputs)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['attempts'], 2)
    
    def test_metrics_tracking(self):
        """Test that generator tracks metrics."""
        inputs = ConsolidatedInput(
            user_intent='Test intent',
            grade_level='High',
            num_objectives=5
        )
        
        with patch('apps.generators.consolidated.generator.route_to_domain') as mock_routing:
            mock_routing.return_value = {
                'domain': 'chemistry',
                'confidence': 0.8,
                'apply_food_overlay': False,
                'domain_description': 'Chemistry'
            }
            
            # Generate multiple times to test metrics
            for _ in range(3):
                self.generator.generate(inputs)
            
            metrics = self.generator.get_metrics()
            
            self.assertEqual(metrics['generations_completed'], 3)
            self.assertEqual(metrics['grade_distribution']['High'], 3)
            self.assertEqual(metrics['domain_distribution']['chemistry'], 3)
            self.assertGreater(metrics['success_rate'], 0)
            self.assertGreater(metrics['average_generation_time'], 0)


class TestOpenAIServiceIntegration(TestCase):
    """Test OpenAI service integration with consolidated system."""
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_consolidated_generation_success(self, mock_openai):
        """Test successful consolidated generation through OpenAI service."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Valid learning objectives output"))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        
        result = service.generate_learning_objectives(
            user_intent='Understand bacterial growth',
            grade_level='Middle',
            num_objectives=5
        )
        
        self.assertIn('content', result)
        self.assertIn('routing_info', result)
        self.assertIn('quality_metrics', result)
        self.assertIn('observability', result)
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_backward_compatibility_fallback(self, mock_openai):
        """Test backward compatibility fallback."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Valid learning objectives output"))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        
        # Test legacy format
        result = service.generate_learning_objectives(
            subject='Science',
            topic='Bacteria',
            grade_level='Middle',
            number_of_objectives=5,
            customization='Focus on temperature'
        )
        
        self.assertIn('content', result)
        # Should work with legacy parameters
        self.assertIsInstance(result, dict)
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_consolidated_failure_with_fallback(self, mock_openai):
        """Test consolidated system failure with fallback to legacy."""
        # Mock OpenAI response
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Fallback learning objectives output"))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        
        result = service.generate_learning_objectives(
            user_intent='Test intent',
            grade_level='High',
            num_objectives=5
        )
        
        # Should succeed with fallback
        self.assertIn('content', result)
        self.assertIn('routing_info', result)
        self.assertTrue(result.get('routing_info', {}).get('fallback_used', False))


class TestIntegrationScenarios(TestCase):
    """Test integration scenarios across different domains and grade levels."""
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_elementary_science_objectives(self, mock_openai):
        """Test elementary science objectives generation."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="""Lesson Objectives

Grade Level: Elementary
Topic: Plant Life Cycle

By the end of this lesson, students will be able to:
1. Identify the stages of a plant life cycle.
2. Describe what plants need to grow.
3. Compare different types of plants.
4. Sort plants by their characteristics.
5. Draw a simple plant life cycle diagram."""))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        result = service.generate_learning_objectives(
            user_intent='Understand the life cycle of plants',
            grade_level='Elementary',
            num_objectives=5
        )
        
        self.assertIn('content', result)
        self.assertIn('objectives', result)
        self.assertEqual(len(result['objectives']), 5)
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_college_mathematics_objectives(self, mock_openai):
        """Test college mathematics objectives generation."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="""Lesson Objectives

Grade Level: College
Topic: Calculus Applications

By the end of this lesson, students will be able to:
1. Formulate optimization problems using calculus principles.
2. Evaluate the efficiency of mathematical models.
3. Defend the choice of integration methods for complex functions.
4. Synthesize multiple calculus techniques to solve real-world problems.
5. Engineer mathematical solutions for engineering applications."""))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        result = service.generate_learning_objectives(
            user_intent='Apply calculus to solve optimization problems',
            grade_level='College',
            num_objectives=5
        )
        
        self.assertIn('content', result)
        self.assertIn('objectives', result)
        # College-level objectives should use advanced verbs
        objectives_text = ' '.join(result['objectives'])
        self.assertIn('Formulate', objectives_text)
        self.assertIn('Evaluate', objectives_text)
        self.assertIn('Defend', objectives_text)
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_food_science_domain_routing(self, mock_openai):
        """Test food science domain routing with overlay."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="""Lesson Objectives

Grade Level: High
Topic: Food Preservation

By the end of this lesson, students will be able to:
1. Analyze factors that contribute to food spoilage.
2. Evaluate different preservation methods.
3. Design a food safety plan for a commercial kitchen.
4. Compare bacterial growth in various food storage conditions.
5. Propose solutions for preventing foodborne illness."""))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        result = service.generate_learning_objectives(
            user_intent='Understand food preservation and safety in commercial kitchens',
            grade_level='High',
            num_objectives=5
        )
        
        self.assertIn('content', result)
        self.assertIn('routing_info', result)
        routing = result['routing_info']
        self.assertEqual(routing['domain'], 'food_science')
        self.assertTrue(routing['apply_food_overlay'])


class TestPerformanceAndQuality(TestCase):
    """Test performance and quality metrics."""
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_generation_time_tracking(self, mock_openai):
        """Test that generation time is tracked."""
        import time
        start_time = time.time()
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Valid output"))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        result = service.generate_learning_objectives(
            user_intent='Test intent',
            grade_level='Middle',
            num_objectives=5
        )
        
        # Should track generation time
        self.assertIn('generation_time', result)
        self.assertIn('observability', result)
        self.assertGreater(result['generation_time'], 0)
        self.assertLess(result['generation_time'], 10)  # Should be reasonable
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_quality_metrics_collection(self, mock_openai):
        """Test quality metrics collection."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="""Lesson Objectives

Grade Level: Middle
Topic: Test Topic

By the end of this lesson, students will be able to:
1. Explain the main concepts clearly.
2. Compare different approaches effectively.
3. Analyze the key factors involved.
4. Evaluate the outcomes critically.
5. Design appropriate solutions."""))]
        )
        mock_openai.return_value = mock_client
        
        service = OpenAIService()
        result = service.generate_learning_objectives(
            user_intent='Test quality metrics',
            grade_level='Middle',
            num_objectives=5
        )
        
        self.assertIn('quality_metrics', result)
        quality = result['quality_metrics']
        
        # Should have objective quality metrics
        self.assertIn('objectives_generated', quality)
        self.assertIn('target_objectives', quality)
        self.assertIn('grade_level_match', quality)
        self.assertIn('domain_confidence', quality)
        self.assertIn('has_food_overlay', quality)


# Regression test fixtures
REGRESSION_TEST_CASES = [
    {
        'name': 'Elementary Plant Science',
        'input': {
            'user_intent': 'Understand how plants grow and need sunlight',
            'grade_level': 'Elementary',
            'num_objectives': 5
        },
        'expected_domain': 'biology',
        'expected_verbs': ['Identify', 'Describe', 'Compare', 'Draw'],
        'avoid_verbs': ['Analyze', 'Evaluate', 'Critique']
    },
    {
        'name': 'Middle School Chemistry',
        'input': {
            'user_intent': 'Understand chemical reactions and balancing equations',
            'grade_level': 'Middle',
            'num_objectives': 5
        },
        'expected_domain': 'chemistry',
        'expected_verbs': ['Explain', 'Compare', 'Calculate'],
        'avoid_verbs': ['Synthesize', 'Formulate', 'Defend']
    },
    {
        'name': 'High School Physics',
        'input': {
            'user_intent': 'Understand motion, forces, and energy in physical systems',
            'grade_level': 'High',
            'num_objectives': 5
        },
        'expected_domain': 'physics',
        'expected_verbs': ['Analyze', 'Evaluate', 'Design'],
        'avoid_verbs': ['Synthesize', 'Formulate', 'Optimize']
    },
    {
        'name': 'College Mathematics',
        'input': {
            'user_intent': 'Apply calculus to solve optimization problems',
            'grade_level': 'College',
            'num_objectives': 5
        },
        'expected_domain': 'mathematics',
        'expected_verbs': ['Formulate', 'Evaluate', 'Defend', 'Synthesize'],
        'avoid_verbs': ['Identify', 'Describe', 'List']
    },
    {
        'name': 'Food Science with Overlay',
        'input': {
            'user_intent': 'Understand bacterial growth in food preservation contexts',
            'grade_level': 'High',
            'num_objectives': 5
        },
        'expected_domain': 'microbiology',
        'expected_verbs': ['Analyze', 'Evaluate', 'Design'],
        'avoid_verbs': ['Understand', 'Learn', 'Know'],
        'expect_food_overlay': True
    }
]


class TestRegressionFixtures(TestCase):
    """Test regression fixtures to ensure consistency."""
    
    @patch('apps.generators.openai_service.openai.OpenAI')
    def test_regression_cases(self, mock_openai):
        """Test all regression cases."""
        for case in REGRESSION_TEST_CASES:
            with self.subTest(case=case['name']):
                # Mock appropriate response based on expected verbs
                mock_response = self._create_mock_response(case)
                
                mock_client = Mock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client
                
                service = OpenAIService()
                result = service.generate_learning_objectives(**case['input'])
                
                # Basic validation
                self.assertIn('content', result, f"Failed case: {case['name']}")
                self.assertIn('routing_info', result, f"Failed case: {case['name']}")
                self.assertIn('objectives', result, f"Failed case: {case['name']}")
                
                # Check domain routing
                routing = result['routing_info']
                self.assertEqual(routing['domain'], case['expected_domain'], 
                               f"Wrong domain for {case['name']}")
                
                # Check food overlay expectation
                if case.get('expect_food_overlay'):
                    self.assertTrue(routing.get('apply_food_overlay', False),
                                  f"Missing food overlay for {case['name']}")
                
                # Check verb appropriateness
                objectives_text = ' '.join(result['objectives'])
                for verb in case['expected_verbs']:
                    self.assertIn(verb, objectives_text, 
                                f"Missing expected verb '{verb}' in {case['name']}")
                
                for verb in case['avoid_verbs']:
                    self.assertNotIn(verb, objectives_text, 
                                   f"Found avoided verb '{verb}' in {case['name']}")
    
    def _create_mock_response(self, case):
        """Create mock response based on test case expectations."""
        # Generate appropriate objectives based on expected verbs
        objectives = []
        for i, verb in enumerate(case['expected_verbs'][:5], 1):
            objectives.append(f"{i}. {verb} the key concepts related to the topic.")
        
        objectives_text = '\n'.join(objectives)
        
        return Mock(
            choices=[Mock(message=Mock(content=f"""Lesson Objectives

Grade Level: {case['input']['grade_level']}
Topic: Test Topic

By the end of this lesson, students will be able to:
{objectives_text}"""))]
        )


if __name__ == '__main__':
    pytest.main([__file__])
