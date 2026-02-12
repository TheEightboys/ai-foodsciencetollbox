# generators/lesson_starter/logic.py
"""
Core logic for the Lesson Starter Ideas generator (v2).

Generates exactly 7 varied, practical, 5-minute lesson starter ideas
with validation and repair loop.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

from ..shared.llm_client import LLMClient
from .prompt import build_lesson_starter_prompt, build_repair_prompt
from .validation import validate_lesson_starter


@dataclass(frozen=True)
class LessonStarterInputs:
    category: str
    topic: str
    grade_level: str
    teacher_details: Optional[str] = None
    time_needed: Optional[str] = None  # Kept for backward compat; ignored (always 5 min)


def generate_lesson_starter(
    llm: LLMClient, 
    inputs: LessonStarterInputs, 
    max_attempts: int = 3
) -> Dict[str, Any]:
    """
    Generate 7 lesson starter ideas with validation and repair loop.
    
    Returns:
        {
            'success': bool,
            'output': str,
            'attempts': int,
            'errors': list
        }
    
    Raises:
        ValueError: If all attempts fail.
    """
    original_prompt = build_lesson_starter_prompt(
        category=inputs.category,
        topic=inputs.topic,
        grade_level=inputs.grade_level,
        teacher_details=inputs.teacher_details,
    )
    
    current_prompt = original_prompt
    last_output = None
    last_errors = []
    
    for attempt in range(1, max_attempts + 1):
        try:
            output = llm.generate_text(current_prompt)
            last_output = output
        except Exception as e:
            if attempt == max_attempts:
                raise ValueError(f"LLM generation failed after {attempt} attempts: {str(e)}")
            continue
        
        is_valid, errors = validate_lesson_starter(
            output=output,
            grade_level=inputs.grade_level,
            teacher_details=inputs.teacher_details,
        )
        
        if is_valid:
            return {
                'success': True,
                'output': output,
                'attempts': attempt,
                'errors': [],
            }
        
        last_errors = errors
        
        if attempt < max_attempts:
            current_prompt = build_repair_prompt(
                original_prompt=original_prompt,
                invalid_output=output,
                validation_errors=errors,
            )
    
    # All attempts failed — still return the best output we have
    raise ValueError(
        f"Generation failed after {max_attempts} attempts.\n"
        f"Final validation errors:\n" + 
        '\n'.join(f"  - {e}" for e in last_errors) +
        f"\n\nFinal output:\n{last_output}"
    )


def generate_lesson_starter_from_dict(
    llm_client: LLMClient = None,
    llm: LLMClient = None,
    inputs: dict = None,
    max_attempts: int = 3,
) -> dict:
    """
    Convenience wrapper — accepts a dict and delegates to generate_lesson_starter.
    Accepts both 'llm_client' and 'llm' kwargs for backward compatibility.
    """
    client = llm_client or llm
    if client is None:
        raise ValueError("An LLM client must be provided (llm_client or llm)")
    if inputs is None:
        inputs = {}

    lesson_inputs = LessonStarterInputs(
        category=inputs.get('category', 'Science'),
        topic=inputs.get('topic', ''),
        grade_level=inputs.get('grade_level', 'High'),
        teacher_details=inputs.get('teacher_details', inputs.get('customization', '')),
    )
    
    return generate_lesson_starter(
        llm=client,
        inputs=lesson_inputs,
        max_attempts=max_attempts,
    )


class LessonStarterGenerator:
    """Legacy generator class for backward compatibility."""
    
    def __init__(self, llm_client=None, max_attempts=3):
        self.llm_client = llm_client
        self.max_attempts = max_attempts
    
    def generate(
        self,
        category: str,
        topic: str,
        grade_level: str,
        time_needed: str = "5 minutes",
        teacher_details: str = None,
    ) -> dict:
        if not self.llm_client:
            raise ValueError("LLM client is required")
        
        inputs = LessonStarterInputs(
            category=category,
            topic=topic,
            grade_level=grade_level,
            teacher_details=teacher_details,
        )
        
        try:
            return generate_lesson_starter(
                llm=self.llm_client,
                inputs=inputs,
                max_attempts=self.max_attempts,
            )
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'attempts': self.max_attempts,
                'errors': [str(e)],
            }
