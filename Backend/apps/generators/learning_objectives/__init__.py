"""
Learning Objectives Generator Module

This module implements a robust learning objectives generation system with:
- Bloom-aligned verb guidance by grade level
- Forbidden verb detection
- Grade-level ceiling/floor validation
- Teacher customization support
- Automatic repair loop for validation failures
- DOCX export with template preservation
- Enhanced food science lens enforcement
- Strict verb validation
- Teacher context incorporation validation
"""

from .logic import (
    generate_learning_objectives, 
    LearningObjectivesInputFinal as GenerationInputs,
    LearningObjectivesGenerator
)
from .prompt import build_generation_prompt_final as build_learning_objectives_prompt, build_generation_prompt, build_repair_prompt
from .validation import validate_learning_objectives_final as validate_learning_objectives_output, validate_learning_objectives

__all__ = [
    'generate_learning_objectives',
    'GenerationInputs',
    'build_learning_objectives_prompt',
    'validate_learning_objectives_output',
    'LearningObjectivesGenerator',
    'build_generation_prompt',
    'build_repair_prompt',
    'validate_learning_objectives',
]
