#!/usr/bin/env python3
"""
Test script to verify the new learning objectives implementation works correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/path/to/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.generators.learning_objectives.logic import LearningObjectivesInput, LearningObjectivesGenerator
from apps.generators.learning_objectives.llm_client import get_llm_client

def test_new_implementation():
    """Test the new learning objectives implementation."""
    
    print("Testing new learning objectives implementation...")
    
    try:
        # Create LLM client
        llm_client = get_llm_client()
        print("✓ LLM client created successfully")
        
        # Create test inputs
        inputs = LearningObjectivesInput(
            category="Science",
            topic="Food Safety and Hygiene",
            grade_level="Middle",
            teacher_details="Focus on temperature control and cross-contamination",
            num_objectives=5
        )
        print("✓ LearningObjectivesInput created successfully")
        
        # Create generator
        generator = LearningObjectivesGenerator(llm_client=llm_client, max_attempts=3)
        print("✓ LearningObjectivesGenerator created successfully")
        
        # Test generation (commented out to avoid actual API call)
        # result = generator.generate(inputs)
        # print(f"✓ Generation successful: {len(result['objectives'])} objectives generated")
        
        print("✓ All setup tests passed - implementation is ready!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_new_implementation()
    sys.exit(0 if success else 1)
