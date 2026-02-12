"""
Learning Objectives Generation Logic - FINAL CONSOLIDATED VERSION
Combines: Optimized performance + Accuracy routing + Improved validation

Key features:
- Reduced max_attempts (2 instead of 3) for speed
- Domain routing for accuracy
- Fast validation with critical/warning separation
"""

from dataclasses import dataclass
from typing import Optional, Dict
from ..shared.llm_client import LLMClient


@dataclass
class LearningObjectivesInputFinal:
    """
    FINAL INPUT MODEL - Simplified for accuracy.
    
    Primary field: user_intent (what teacher wants students to learn)
    Grade level: drives complexity
    """
    user_intent: str  # Required: Natural language learning goal
    grade_level: str  # Required: Elementary, Middle, High, College
    num_objectives: int = 5  # Optional: 4-10, default 5
    
    def __post_init__(self):
        """Validate inputs."""
        if self.grade_level not in ['Elementary', 'Middle', 'High', 'College']:
            raise ValueError(f"Invalid grade_level: {self.grade_level}")
        
        if not (4 <= self.num_objectives <= 10):
            raise ValueError(f"num_objectives must be 4-10, got {self.num_objectives}")
        
        if not self.user_intent or not self.user_intent.strip():
            raise ValueError("user_intent is required")
        
        if len(self.user_intent.strip()) < 10:
            raise ValueError("user_intent must be at least 10 characters")


# Backward compatibility
@dataclass
class LearningObjectivesInput:
    """DEPRECATED: Use LearningObjectivesInputFinal instead."""
    category: str
    topic: str
    grade_level: str
    teacher_details: Optional[str] = None
    num_objectives: int = 5
    
    def __post_init__(self):
        if self.grade_level not in ['Elementary', 'Middle', 'High', 'College']:
            raise ValueError(f"Invalid grade_level: {self.grade_level}")
        if not (4 <= self.num_objectives <= 10):
            raise ValueError(f"num_objectives must be 4-10, got {self.num_objectives}")


class LearningObjectivesGeneratorFinal:
    """
    FINAL CONSOLIDATED generator with all optimizations.
    
    Improvements:
    1. Reduced max_attempts from 3 to 2 (performance)
    2. Uses domain routing for accuracy
    3. Fast validation separates critical/warnings
    4. Only retries on critical errors
    """
    
    def __init__(self, llm_client: LLMClient, max_attempts: int = 2):
        """
        Initialize generator.
        
        Args:
            llm_client: LLM client for generation
            max_attempts: Max attempts (default 2, optimized from 3)
        """
        self.llm_client = llm_client
        self.max_attempts = max_attempts
    
    def generate(self, inputs: LearningObjectivesInputFinal) -> Dict:
        """
        Generate learning objectives with domain routing and fast validation.
        
        Args:
            inputs: Generation parameters
        
        Returns:
            {
                'success': bool,
                'grade_level': str,
                'topic': str,
                'objectives': List[str],
                'rendered_text': str,
                'attempts': int,
                'warnings': list,
                'errors': list,
                'routing': dict  # Domain routing info
            }
        """
        
        # Import here to avoid circular deps
        from domain_routing import route_to_domain
        from prompt import build_generation_prompt_final, build_repair_prompt
        from validation import validate_learning_objectives_final
        
        # Route to appropriate domain
        routing_result = route_to_domain(
            user_intent=inputs.user_intent,
            grade_level=inputs.grade_level,
            category=None
        )
        
        # Build initial prompt with routing
        original_prompt = build_generation_prompt_final(
            user_intent=inputs.user_intent,
            grade_level=inputs.grade_level,
            routing_result=routing_result,
            num_objectives=inputs.num_objectives
        )
        
        current_prompt = original_prompt
        last_output = None
        last_errors = []
        all_warnings = []
        
        for attempt in range(1, self.max_attempts + 1):
            # Generate
            try:
                output = self.llm_client.generate_text(current_prompt)
                last_output = output
            except Exception as e:
                if attempt == self.max_attempts:
                    raise ValueError(f"LLM generation failed: {str(e)}")
                continue
            
            # Validate (fast version with critical/warning separation)
            result, critical_errors, warnings = validate_learning_objectives_final(
                output=output,
                grade_level=inputs.grade_level,
                user_intent=inputs.user_intent
            )
            
            all_warnings.extend(warnings)
            
            if result:
                # Success!
                return {
                    'success': True,
                    'grade_level': result['grade_level'],
                    'topic': result['topic'],
                    'objectives': result['objectives'],
                    'rendered_text': result['rendered_text'],
                    'attempts': attempt,
                    'warnings': all_warnings,
                    'errors': [],
                    'routing': routing_result  # Include routing info
                }
            
            last_errors = critical_errors
            
            # Only retry on CRITICAL errors
            if attempt < self.max_attempts:
                current_prompt = build_repair_prompt(
                    original_prompt=original_prompt,
                    invalid_output=output,
                    validation_errors=critical_errors
                )
        
        # Failed
        raise ValueError(
            f"Generation failed after {self.max_attempts} attempts.\n"
            f"Errors:\n" + '\n'.join(f"  - {e}" for e in last_errors)
        )
    
    def generate_legacy(self, inputs: LearningObjectivesInput) -> Dict:
        """
        Generate using legacy input format.
        Converts to new format internally.
        """
        # Convert legacy to new format
        user_intent = inputs.teacher_details if inputs.teacher_details else inputs.topic
        
        new_inputs = LearningObjectivesInputFinal(
            user_intent=user_intent,
            grade_level=inputs.grade_level,
            num_objectives=inputs.num_objectives
        )
        
        return self.generate(new_inputs)


# Backward compatibility
class LearningObjectivesGenerator(LearningObjectivesGeneratorFinal):
    """Backward compatible class name."""
    pass


def generate_learning_objectives(
    llm_client: LLMClient,
    inputs: LearningObjectivesInputFinal,
    max_attempts: int = 2
) -> Dict:
    """
    Convenience function to generate learning objectives.
    
    Args:
        llm_client: LLM client
        inputs: Generation parameters
        max_attempts: Max attempts (default 2)
    
    Returns:
        Result dict with objectives, routing info, warnings
    """
    generator = LearningObjectivesGeneratorFinal(llm_client, max_attempts)
    return generator.generate(inputs)
