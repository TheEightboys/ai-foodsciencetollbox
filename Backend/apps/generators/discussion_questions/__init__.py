"""
Discussion Questions Generator Module (v2)

Generates exactly 5 concept-deepening discussion questions
with "Option N" format, food science lens, and teacher cue facilitation.
Includes validation and auto-repair loop (up to 3 attempts).
"""

from .logic import DiscussionQuestionsInput, DiscussionQuestionsGenerator, generate_discussion_questions_from_dict
from .prompt import build_generation_prompt, build_repair_prompt
from .validation import validate_discussion_questions

__all__ = [
    'generate_discussion_questions_from_dict',
    'DiscussionQuestionsInput',
    'DiscussionQuestionsGenerator',
    'build_generation_prompt',
    'build_repair_prompt',
    'validate_discussion_questions',
]
