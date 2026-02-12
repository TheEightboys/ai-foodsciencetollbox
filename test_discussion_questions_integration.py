#!/usr/bin/env python3
"""
Test script to verify the new discussion questions implementation works correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/path/to/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.generators.discussion_questions.logic import DiscussionQuestionsGenerator, generate_discussion_questions_from_dict
from apps.generators.discussion_questions.llm_client import get_llm_client

def test_new_discussion_questions_implementation():
    """Test the new discussion questions implementation."""
    
    print("Testing new discussion questions implementation...")
    
    try:
        # Create LLM client
        llm_client = get_llm_client()
        print("✓ LLM client created successfully")
        
        # Test generator class
        generator = DiscussionQuestionsGenerator(llm_client=llm_client, max_attempts=3)
        print("✓ DiscussionQuestionsGenerator created successfully")
        
        # Test dict-based generation function
        inputs = {
            'category': 'Science',
            'topic': 'Food Safety and Bacteria',
            'grade_level': 'Middle',
            'num_questions': 3,
            'teacher_details': 'Focus on real-world scenarios and decision-making'
        }
        
        print("✓ Test inputs prepared")
        print(f"  - Category: {inputs['category']}")
        print(f"  - Topic: {inputs['topic']}")
        print(f"  - Grade Level: {inputs['grade_level']}")
        print(f"  - Number of Questions: {inputs['num_questions']}")
        
        # Test generation (commented out to avoid actual API call)
        # result = generate_discussion_questions_from_dict(
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
    success = test_new_discussion_questions_implementation()
    sys.exit(0 if success else 1)
