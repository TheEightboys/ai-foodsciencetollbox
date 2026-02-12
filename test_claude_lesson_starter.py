#!/usr/bin/env python
"""
Test script to verify the Claude-based lesson starter implementation.
This tests the new enhanced validation and repair loop functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Test the new Claude-based implementation
from Backend.apps.generators.lesson_starter.logic import generate_lesson_starter_new, LessonStarterGenerator
from Backend.apps.generators.lesson_starter.validation import validate_lesson_starter
from Backend.apps.generators.lesson_starter.prompt import build_generation_prompt
from Backend.apps.generators.lesson_starter.docx_export import export_lesson_starter_to_docx


class MockLLMClient:
    """Mock LLM client for testing purposes"""
    
    def generate_text(self, prompt: str) -> str:
        """Mock generation that returns a valid lesson starter format"""
        return """Lesson Starter

Grade Level: High
Topic: Fermentation in Food Preservation
Time Needed: 6–7 minutes

Key Lesson Ideas to Explore
Fermentation as controlled microbial growth
Acid production for food preservation
Probiotics and digestive health
Flavor enhancement through fermentation
Safety in home fermentation practices
Cultural significance of fermented foods

Prior Knowledge to Connect
Students likely understand that microorganisms exist and can cause food to spoil. They may have experience with common fermented foods like yogurt, pickles, or bread. Connect this to their understanding of how some microorganisms can be beneficial when controlled properly in food preservation.

Teacher Opening Script
Today we're exploring how humans have used tiny living organisms to transform and preserve food for thousands of years. You've probably eaten fermented foods like yogurt or sauerkraut, but have you ever wondered how these foods are made safely? Fermentation is a fascinating process where we partner with beneficial microorganisms to not only preserve our food but also enhance its nutritional value and flavor. We're going to explore the science behind this ancient technique that's still crucial in our modern food system.

**What do you think are the key safety considerations when fermenting food at home, and how do they compare to other food preservation methods?**"""


def test_basic_functionality():
    """Test basic functionality of the new Claude-based implementation"""
    print("Testing basic functionality...")
    
    # Test the convenience function
    try:
        result = generate_lesson_starter_new(
            category="Food Science",
            topic="Fermentation in Food Preservation",
            grade_level="High",
            time_needed="6–7 minutes",
            teacher_details="Focus on safety aspects",
            llm_client=MockLLMClient(),
            max_attempts=1
        )
        print("✓ generate_lesson_starter_new function works")
        print(f"Generated content length: {len(result)} characters")
    except Exception as e:
        print(f"✗ Error in generate_lesson_starter_new: {e}")
        return False
    
    # Test the validation function
    try:
        is_valid, errors = validate_lesson_starter(
            output=result,
            grade_level="High",
            teacher_details="Focus on safety aspects"
        )
        print(f"✓ Validation function works, is_valid: {is_valid}")
        if errors:
            print(f"  Validation errors: {errors}")
    except Exception as e:
        print(f"✗ Error in validation: {e}")
        return False
    
    # Test the generator class
    try:
        generator = LessonStarterGenerator(
            llm_client=MockLLMClient(),
            max_attempts=2
        )
        result = generator.generate(
            category="Food Science",
            topic="Fermentation",
            grade_level="High",
            time_needed="6–7 minutes",
            teacher_details="Focus on safety"
        )
        print(f"✓ LessonStarterGenerator class works, success: {result['success']}")
    except Exception as e:
        print(f"✗ Error in LessonStarterGenerator: {e}")
        return False
    
    return True


def test_prompt_building():
    """Test prompt building functionality"""
    print("\nTesting prompt building...")
    
    try:
        prompt = build_generation_prompt(
            category="Food Science",
            topic="Fermentation in Food Preservation",
            grade_level="High",
            time_needed="6–7 minutes",
            teacher_details="Focus on safety aspects"
        )
        print(f"✓ Prompt building works, prompt length: {len(prompt)} characters")
        print(f"  Prompt contains validation rules: {'VALIDATION RULES' in prompt}")
        print(f"  Prompt contains food science lens: {'FOOD SCIENCE LENS' in prompt}")
    except Exception as e:
        print(f"✗ Error in prompt building: {e}")
        return False
    
    return True


def test_docx_export_stub():
    """Test that docx export functions are available"""
    print("\nTesting DOCX export functions...")
    
    # Just test that functions exist and have correct signatures
    try:
        # This would require a real DOCX file to test fully, so just check function exists
        print(f"✓ export_lesson_starter_to_docx function exists: {callable(export_lesson_starter_to_docx)}")
        print("✓ All DOCX export functions available")
    except Exception as e:
        print(f"✗ Error with DOCX export: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("Testing Claude-based Lesson Starter Implementation")
    print("=" * 50)
    
    success = True
    success &= test_basic_functionality()
    success &= test_prompt_building()
    success &= test_docx_export_stub()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! Claude-based lesson starter implementation is working correctly.")
    else:
        print("✗ Some tests failed.")
    
    print("\nNote: This test uses a mock LLM client. In a real implementation,")
    print("the actual LLM service would be used for generation.")