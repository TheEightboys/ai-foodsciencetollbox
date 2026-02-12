#!/usr/bin/env python3
"""
Comprehensive unit tests for all three generators.
Tests the standard format, error handling, and validation logic.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

# Mock Django before importing
sys.modules['django'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
sys.modules['django.http'] = MagicMock()
sys.modules['django.views'] = MagicMock()
sys.modules['django.views.decorators'] = MagicMock()
sys.modules['django.views.decorators.http'] = MagicMock()
sys.modules['django.views.decorators.csrf'] = MagicMock()

# Now import the generators
from apps.generators.discussion_questions.logic import (
    DiscussionQuestionsGenerator,
    DiscussionQuestionsInput,
    generate_discussion_questions_from_dict
)
from apps.generators.discussion_questions.validation import validate_discussion_questions

from apps.generators.lesson_starter.logic import (
    generate_lesson_starter,
    generate_lesson_starter_from_dict,
    LessonStarterInputs
)
from apps.generators.lesson_starter.validation import validate_lesson_starter

from apps.generators.learning_objectives.logic import (
    LearningObjectivesGenerator,
    LearningObjectivesInput,
    generate_learning_objectives
)
from apps.generators.learning_objectives.validation import validate_learning_objectives


class TestDiscussionQuestionsFormat(unittest.TestCase):
    """Test Discussion Questions follow standard format."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.generator = DiscussionQuestionsGenerator(llm_client=self.mock_llm, max_attempts=3)
    
    def test_valid_discussion_questions_format(self):
        """Test that valid discussion questions pass validation."""
        valid_output = """**Grade Level**: Middle
**Topic**: Food Safety

1. What evidence would you use to decide if leftovers in the fridge are still safe to eat, and how confident are you in your decision?
**Teacher cue**: Listen for students considering color, smell, and storage time.

2. How would you compare the risks of cross-contamination when handling raw chicken versus vegetables in a typical kitchen?
**Teacher cue**: Push for specific scenarios like raw chicken touching vegetables.

3. What tradeoffs exist between food safety and food waste when deciding to throw away questionable leftovers?
**Teacher cue**: Prompt for discussion about cost, environmental impact, and health risk."""
        
        is_valid, errors = validate_discussion_questions(
            output=valid_output,
            num_questions=3,
            grade_level='Middle'
        )
        
        self.assertTrue(is_valid, f"Valid format should pass validation. Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_discussion_questions_missing_grade_level(self):
        """Test that missing Grade Level is caught."""
        invalid_output = """**Topic**: Food Safety

1. What evidence would you use to decide if leftovers are safe?
**Teacher cue**: Listen for considerations."""
        
        is_valid, errors = validate_discussion_questions(
            output=invalid_output,
            num_questions=1,
            grade_level='Middle'
        )
        
        self.assertFalse(is_valid)
        self.assertTrue(any('Grade Level' in e for e in errors))
    
    def test_discussion_questions_wrong_question_count(self):
        """Test that wrong number of questions is caught."""
        invalid_output = """**Grade Level**: Middle
**Topic**: Food Safety

1. What evidence would you use to decide if leftovers are safe?
**Teacher cue**: Listen for considerations."""
        
        is_valid, errors = validate_discussion_questions(
            output=invalid_output,
            num_questions=3,  # Expecting 3, but only 1 provided
            grade_level='Middle'
        )
        
        self.assertFalse(is_valid)
        self.assertTrue(any('Expected exactly 3 questions' in e for e in errors))
    
    def test_discussion_questions_return_format(self):
        """Test that generator returns correct dict format."""
        valid_output = """**Grade Level**: Middle
**Topic**: Food Safety

1. What evidence would you use to decide if leftovers are safe?
**Teacher cue**: Listen for considerations."""
        
        self.mock_llm.generate_text.return_value = valid_output
        
        inputs = DiscussionQuestionsInput(
            category='Science',
            topic='Food Safety',
            grade_level='Middle',
            num_questions=1
        )
        
        result = self.generator.generate(inputs)
        
        # Check return format
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('output', result)
        self.assertIn('attempts', result)
        self.assertIn('errors', result)
        self.assertTrue(result['success'])
        self.assertEqual(result['attempts'], 1)
        self.assertEqual(len(result['errors']), 0)


class TestLessonStarterFormat(unittest.TestCase):
    """Test Lesson Starter follows standard format."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
    
    def test_valid_lesson_starter_format(self):
        """Test that valid lesson starter passes validation."""
        valid_output = """Lesson Starter

Grade Level: Middle
Topic: Food Storage
Time Needed: 6-7 minutes

Key Lesson Ideas to Explore
Bacteria growth influenced by temperature
Food preservation through refrigeration
Cross-contamination risks in kitchens
Shelf life and expiration dates
Quality assessment of stored foods
Storage containers and food safety

Prior Knowledge to Connect
Students likely recall keeping milk in the fridge and leftovers from dinner. Listen for misconceptions about how long food stays safe. Quick move: ask them about a specific leftover they've seen at home.

Teacher Opening Script
Imagine you open your fridge and find a container of pizza from three days ago. You're hungry, but you're not sure if it's still safe to eat. What would you do? Most of us have faced this decision. The pizza looks okay, but looks can be deceiving. Food safety isn't just about what we see—it's about invisible bacteria and how they grow under different conditions. In a warm kitchen, bacteria multiply rapidly, but in a cold fridge, they slow down dramatically. Understanding these invisible processes helps us make better decisions about what to keep and what to throw away. Every day, families around the world make these choices, balancing food waste with food safety.

**What evidence would you use to decide if that pizza is still safe to eat?**"""
        
        is_valid, errors = validate_lesson_starter(
            output=valid_output,
            grade_level='Middle'
        )
        
        self.assertTrue(is_valid, f"Valid format should pass validation. Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_lesson_starter_missing_required_sections(self):
        """Test that missing required sections are caught."""
        invalid_output = """Lesson Starter

Grade Level: Middle
Topic: Food Storage

Key Lesson Ideas to Explore
Bacteria growth influenced by temperature"""
        
        is_valid, errors = validate_lesson_starter(
            output=invalid_output,
            grade_level='Middle'
        )
        
        self.assertFalse(is_valid)
        self.assertTrue(any('Prior Knowledge' in e or 'Teacher Opening' in e for e in errors))
    
    def test_lesson_starter_return_format(self):
        """Test that generator returns correct dict format."""
        valid_output = """Lesson Starter

Grade Level: Middle
Topic: Food Storage
Time Needed: 6-7 minutes

Key Lesson Ideas to Explore
Bacteria growth influenced by temperature
Food preservation through refrigeration
Cross-contamination risks in kitchens
Shelf life and expiration dates
Quality assessment of stored foods
Storage containers and food safety

Prior Knowledge to Connect
Students likely recall keeping milk in the fridge. Listen for misconceptions about food safety. Quick move: ask about a specific leftover.

Teacher Opening Script
Imagine you open your fridge and find pizza from three days ago. You're hungry, but unsure if it's safe. Most of us have faced this decision. The pizza looks okay, but looks can be deceiving. Food safety isn't just about appearance—it's about invisible bacteria and how they grow. In a warm kitchen, bacteria multiply rapidly, but in a cold fridge, they slow down. Understanding these processes helps us make better decisions about food waste and safety. Every day, families make these choices, balancing waste with safety concerns.

**What evidence would you use to decide if that pizza is still safe to eat?**"""
        
        self.mock_llm.generate_text.return_value = valid_output
        
        inputs = LessonStarterInputs(
            category='Science',
            topic='Food Storage',
            grade_level='Middle',
            time_needed='6-7 minutes',
            teacher_details=None
        )
        
        result = generate_lesson_starter(
            llm=self.mock_llm,
            inputs=inputs,
            max_attempts=3
        )
        
        # Check return format
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('output', result)
        self.assertIn('attempts', result)
        self.assertIn('errors', result)
        self.assertTrue(result['success'])
        self.assertEqual(result['attempts'], 1)
        self.assertEqual(len(result['errors']), 0)
    
    def test_lesson_starter_from_dict(self):
        """Test generate_lesson_starter_from_dict function."""
        valid_output = """Lesson Starter

Grade Level: Middle
Topic: Food Storage
Time Needed: 6-7 minutes

Key Lesson Ideas to Explore
Bacteria growth influenced by temperature
Food preservation through refrigeration
Cross-contamination risks in kitchens
Shelf life and expiration dates
Quality assessment of stored foods
Storage containers and food safety

Prior Knowledge to Connect
Students likely recall keeping milk in the fridge. Listen for misconceptions about food safety. Quick move: ask about a specific leftover.

Teacher Opening Script
Imagine you open your fridge and find pizza from three days ago. You're hungry, but unsure if it's safe. Most of us have faced this decision. The pizza looks okay, but looks can be deceiving. Food safety isn't just about appearance—it's about invisible bacteria and how they grow. In a warm kitchen, bacteria multiply rapidly, but in a cold fridge, they slow down. Understanding these processes helps us make better decisions about food waste and safety. Every day, families make these choices, balancing waste with safety concerns.

**What evidence would you use to decide if that pizza is still safe to eat?**"""
        
        self.mock_llm.generate_text.return_value = valid_output
        
        inputs_dict = {
            'category': 'Science',
            'topic': 'Food Storage',
            'grade_level': 'Middle',
            'time_needed': '6-7 minutes'
        }
        
        result = generate_lesson_starter_from_dict(
            llm_client=self.mock_llm,
            inputs=inputs_dict,
            max_attempts=3
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['attempts'], 1)


class TestLearningObjectivesFormat(unittest.TestCase):
    """Test Learning Objectives follow standard format."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.generator = LearningObjectivesGenerator(llm_client=self.mock_llm, max_attempts=3)
    
    def test_valid_learning_objectives_format(self):
        """Test that valid learning objectives pass validation."""
        valid_output = """Lesson Objectives

Grade Level: Middle
Topic: Food Safety

By the end of this lesson, students will be able to:
1. Identify critical control points in food storage and handling.
2. Analyze how temperature affects bacterial growth in refrigerated foods.
3. Evaluate food safety risks in cross-contamination scenarios.
4. Compare preservation methods and their effectiveness in extending shelf life.
5. Justify decisions about whether to keep or discard questionable food items."""
        
        is_valid, result = validate_learning_objectives(
            output=valid_output,
            grade_level='Middle'
        )
        
        self.assertIsNotNone(result, f"Valid format should pass validation. Errors: {is_valid}")
        self.assertTrue(result is not None)
    
    def test_learning_objectives_missing_lead_in(self):
        """Test that missing lead-in line is caught."""
        invalid_output = """Lesson Objectives

Grade Level: Middle
Topic: Food Safety

1. Identify critical control points in food storage.
2. Analyze how temperature affects bacterial growth."""
        
        is_valid, errors = validate_learning_objectives(
            output=invalid_output,
            grade_level='Middle'
        )
        
        self.assertIsNone(is_valid)
        self.assertTrue(any('By the end' in e for e in errors))
    
    def test_learning_objectives_forbidden_verbs(self):
        """Test that forbidden verbs are caught."""
        invalid_output = """Lesson Objectives

Grade Level: Middle
Topic: Food Safety

By the end of this lesson, students will be able to:
1. Understand food safety principles.
2. Learn about bacterial growth.
3. Know the importance of refrigeration."""
        
        is_valid, errors = validate_learning_objectives(
            output=invalid_output,
            grade_level='Middle'
        )
        
        self.assertIsNone(is_valid)
        self.assertTrue(any('understand' in str(e).lower() or 'learn' in str(e).lower() for e in errors))
    
    def test_learning_objectives_return_format(self):
        """Test that generator returns correct dict format."""
        valid_output = """Lesson Objectives

Grade Level: Middle
Topic: Food Safety

By the end of this lesson, students will be able to:
1. Identify critical control points in food storage and handling.
2. Analyze how temperature affects bacterial growth in refrigerated foods.
3. Evaluate food safety risks in cross-contamination scenarios.
4. Compare preservation methods and their effectiveness in extending shelf life.
5. Justify decisions about whether to keep or discard questionable food items."""
        
        self.mock_llm.generate_text.return_value = valid_output
        
        inputs = LearningObjectivesInput(
            category='Science',
            topic='Food Safety',
            grade_level='Middle',
            num_objectives=5
        )
        
        result = self.generator.generate(inputs)
        
        # Check return format
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('grade_level', result)
        self.assertIn('topic', result)
        self.assertIn('objectives', result)
        self.assertIn('rendered_text', result)
        self.assertIn('attempts', result)
        self.assertIn('errors', result)
        self.assertTrue(result['success'])
        self.assertEqual(result['attempts'], 1)
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['objectives']), 5)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across all generators."""
    
    def test_discussion_questions_llm_failure(self):
        """Test Discussion Questions handles LLM failure."""
        mock_llm = Mock()
        mock_llm.generate_text.side_effect = Exception("LLM API error")
        
        generator = DiscussionQuestionsGenerator(llm_client=mock_llm, max_attempts=1)
        
        inputs = DiscussionQuestionsInput(
            category='Science',
            topic='Food Safety',
            grade_level='Middle',
            num_questions=1
        )
        
        with self.assertRaises(ValueError) as context:
            generator.generate(inputs)
        
        self.assertIn("LLM generation failed", str(context.exception))
    
    def test_lesson_starter_llm_failure(self):
        """Test Lesson Starter handles LLM failure."""
        mock_llm = Mock()
        mock_llm.generate_text.side_effect = Exception("LLM API error")
        
        inputs = LessonStarterInputs(
            category='Science',
            topic='Food Storage',
            grade_level='Middle',
            time_needed='6-7 minutes',
            teacher_details=None
        )
        
        with self.assertRaises(ValueError) as context:
            generate_lesson_starter(llm=mock_llm, inputs=inputs, max_attempts=1)
        
        self.assertIn("LLM generation failed", str(context.exception))
    
    def test_learning_objectives_llm_failure(self):
        """Test Learning Objectives handles LLM failure."""
        mock_llm = Mock()
        mock_llm.generate_text.side_effect = Exception("LLM API error")
        
        generator = LearningObjectivesGenerator(llm_client=mock_llm, max_attempts=1)
        
        inputs = LearningObjectivesInput(
            category='Science',
            topic='Food Safety',
            grade_level='Middle',
            num_objectives=5
        )
        
        with self.assertRaises(ValueError) as context:
            generator.generate(inputs)
        
        self.assertIn("LLM generation failed", str(context.exception))


class TestInputValidation(unittest.TestCase):
    """Test input validation."""
    
    def test_discussion_questions_invalid_grade_level(self):
        """Test Discussion Questions rejects invalid grade level."""
        with self.assertRaises(ValueError) as context:
            DiscussionQuestionsInput(
                category='Science',
                topic='Food Safety',
                grade_level='InvalidLevel',
                num_questions=3
            )
        
        self.assertIn("Invalid grade_level", str(context.exception))
    
    def test_discussion_questions_invalid_num_questions(self):
        """Test Discussion Questions rejects invalid num_questions."""
        with self.assertRaises(ValueError) as context:
            DiscussionQuestionsInput(
                category='Science',
                topic='Food Safety',
                grade_level='Middle',
                num_questions=10  # Too many
            )
        
        self.assertIn("num_questions must be 1-5", str(context.exception))
    
    def test_learning_objectives_invalid_num_objectives(self):
        """Test Learning Objectives rejects invalid num_objectives."""
        with self.assertRaises(ValueError) as context:
            LearningObjectivesInput(
                category='Science',
                topic='Food Safety',
                grade_level='Middle',
                num_objectives=10  # Too many
            )
        
        self.assertIn("num_objectives must be 4-6", str(context.exception))


class TestDictInputConversion(unittest.TestCase):
    """Test dict input conversion."""
    
    def test_discussion_questions_from_dict(self):
        """Test Discussion Questions dict conversion."""
        mock_llm = Mock()
        valid_output = """**Grade Level**: Middle
**Topic**: Food Safety

1. What evidence would you use to decide if leftovers are safe?
**Teacher cue**: Listen for considerations."""
        
        mock_llm.generate_text.return_value = valid_output
        
        inputs_dict = {
            'category': 'Science',
            'topic': 'Food Safety',
            'grade_level': 'Middle',
            'num_questions': 1
        }
        
        result = generate_discussion_questions_from_dict(
            llm_client=mock_llm,
            inputs=inputs_dict,
            max_attempts=3
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['attempts'], 1)
    
    def test_lesson_starter_from_dict_with_customization(self):
        """Test Lesson Starter dict conversion with customization field."""
        mock_llm = Mock()
        valid_output = """Lesson Starter

Grade Level: Middle
Topic: Food Storage
Time Needed: 6-7 minutes

Key Lesson Ideas to Explore
Bacteria growth influenced by temperature
Food preservation through refrigeration
Cross-contamination risks in kitchens
Shelf life and expiration dates
Quality assessment of stored foods
Storage containers and food safety

Prior Knowledge to Connect
Students likely recall keeping milk in the fridge. Listen for misconceptions about food safety. Quick move: ask about a specific leftover.

Teacher Opening Script
Imagine you open your fridge and find pizza from three days ago. You're hungry, but unsure if it's safe. Most of us have faced this decision. The pizza looks okay, but looks can be deceiving. Food safety isn't just about appearance—it's about invisible bacteria and how they grow. In a warm kitchen, bacteria multiply rapidly, but in a cold fridge, they slow down. Understanding these processes helps us make better decisions about food waste and safety. Every day, families make these choices, balancing waste with safety concerns.

**What evidence would you use to decide if that pizza is still safe to eat?**"""
        
        mock_llm.generate_text.return_value = valid_output
        
        inputs_dict = {
            'category': 'Science',
            'topic': 'Food Storage',
            'grade_level': 'Middle',
            'time_needed': '6-7 minutes',
            'customization': 'Focus on real-world scenarios'
        }
        
        result = generate_lesson_starter_from_dict(
            llm_client=mock_llm,
            inputs=inputs_dict,
            max_attempts=3
        )
        
        self.assertTrue(result['success'])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
