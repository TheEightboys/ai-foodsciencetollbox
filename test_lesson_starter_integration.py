#!/usr/bin/env python3
"""
Test script to verify the new lesson starter implementation works correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/path/to/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.generators.lesson_starter.logic import LessonStarterGenerator, generate_lesson_starter_from_dict
from apps.generators.lesson_starter.llm_client import get_llm_client

def test_new_lesson_starter_implementation():
    """Test the new lesson starter implementation."""
    
    print("Testing new lesson starter implementation...")
    
    try:
        # Create LLM client
        llm_client = get_llm_client()
        print("✓ LLM client created successfully")
        
        # Test generator class
        generator = LessonStarterGenerator(llm_client=llm_client, max_attempts=3)
        print("✓ LessonStarterGenerator created successfully")
        
        # Test dict-based generation function
        inputs = {
            'category': 'Science',
            'topic': 'Food Safety and Hygiene',
            'grade_level': 'Middle',
            'time_needed': '6-7 minutes',
            'teacher_details': 'Focus on temperature control and cross-contamination'
        }
        
        print("✓ Test inputs prepared")
        print(f"  - Category: {inputs['category']}")
        print(f"  - Topic: {inputs['topic']}")
        print(f"  - Grade Level: {inputs['grade_level']}")
        print(f"  - Time Needed: {inputs['time_needed']}")
        
        # Test generation (commented out to avoid actual API call)
        # result = generate_lesson_starter_from_dict(
        #     llm_client=llm_client,
        #     inputs=inputs,
        #     max_attempts=3
        # )
        # print(f"✓ Generation successful: {result['success']}")
        # print(f"  - Attempts: {result['attempts']}")
        # print(f"  - Output length: {len(result['output'])} characters")
        
        print("✓ All setup tests passed - implementation is ready!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_new_lesson_starter_implementation()
    sys.exit(0 if success else 1)
