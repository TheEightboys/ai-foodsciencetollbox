"""
Consolidated Generator Module - CANONICAL IMPLEMENTATION
This module brings together all improvements in a single, cohesive system:

Components:
- grade_profiles: Comprehensive grade-level complexity descriptors
- generator: Consolidated generator with domain routing and observability
- validator: Comprehensive validation pipeline with critical/warning separation

Key Features:
- Single-prompt design with user_intent
- Domain routing for accuracy-first approach
- Grade profiles with detailed complexity descriptors
- Strict validation with critical/warning separation
- Performance optimization (2 attempts max)
- Comprehensive observability and metrics
- Post-processing pipeline
"""

from .grade_profiles import (
    GradeProfile,
    get_grade_profile,
    get_grade_verbs,
    validate_grade_appropriateness,
    GRADE_PROFILES
)

from .generator import (
    ConsolidatedInput,
    ConsolidatedGenerator,
    LLMClient,
    generate_consolidated_learning_objectives
)

from .validator import (
    ValidationResult,
    ConsolidatedValidator,
    validate_consolidated_learning_objectives
)

__all__ = [
    # Grade profiles
    'GradeProfile',
    'get_grade_profile',
    'get_grade_verbs',
    'validate_grade_appropriateness',
    'GRADE_PROFILES',
    
    # Generator
    'ConsolidatedInput',
    'ConsolidatedGenerator',
    'LLMClient',
    'generate_consolidated_learning_objectives',
    
    # Validator
    'ValidationResult',
    'ConsolidatedValidator',
    'validate_consolidated_learning_objectives'
]

# Version info
__version__ = '1.0.0'
__description__ = 'Consolidated Learning Objectives Generator with Domain Routing and Grade Profiles'
