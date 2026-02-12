"""
Lesson Starter Ideas Generator Module (v2)

Generates exactly 7 varied, practical, 5-minute lesson starter ideas
with food science lens enforcement, grade-level differentiation,
and idea variety validation.
"""

from .logic import generate_lesson_starter, LessonStarterInputs, generate_lesson_starter_from_dict, LessonStarterGenerator
from .prompt import build_lesson_starter_prompt
from .validation import validate_lesson_starter
from .docx_export import export_lesson_starter_to_docx, export_to_docx

__all__ = [
    'generate_lesson_starter',
    'LessonStarterInputs',
    'generate_lesson_starter_from_dict',
    'build_lesson_starter_prompt',
    'validate_lesson_starter',
    'LessonStarterGenerator',
    'export_lesson_starter_to_docx',
    'export_to_docx',
]
