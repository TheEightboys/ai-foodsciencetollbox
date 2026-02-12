"""
Discussion Questions Generation Logic (v2)
Generates exactly 5 concept-deepening discussion questions
with "Option N" format, validation, and auto-repair loop.
"""

from dataclasses import dataclass
from typing import Optional
from ..shared.llm_client import LLMClient
from .prompt import build_generation_prompt, build_repair_prompt
from .validation import validate_discussion_questions


@dataclass
class DiscussionQuestionsInput:
    """Input parameters for discussion questions generation."""
    category: str
    topic: str
    grade_level: str
    num_questions: int = 5  # Hardcoded to 5
    teacher_details: Optional[str] = None

    def __post_init__(self):
        if self.grade_level not in ('Elementary', 'Middle', 'High', 'College'):
            raise ValueError(f"Invalid grade_level: {self.grade_level}")
        # Always force 5 questions
        self.num_questions = 5


class DiscussionQuestionsGenerator:
    """Main generator with validation and repair loop (up to 3 attempts)."""

    def __init__(self, llm_client: LLMClient, max_attempts: int = 3):
        self.llm_client = llm_client
        self.max_attempts = max_attempts

    def generate(self, inputs: DiscussionQuestionsInput) -> dict:
        original_prompt = build_generation_prompt(
            category=inputs.category,
            topic=inputs.topic,
            grade_level=inputs.grade_level,
            num_questions=inputs.num_questions,
            teacher_details=inputs.teacher_details,
        )

        current_prompt = original_prompt
        last_output = None
        last_errors: list[str] = []

        for attempt in range(1, self.max_attempts + 1):
            try:
                output = self.llm_client.generate_text(current_prompt)
                last_output = output
            except (PermissionError, RuntimeError):
                # Rate-limited or all models failed — no point retrying
                raise
            except Exception as e:
                if attempt == self.max_attempts:
                    raise ValueError(
                        f"LLM generation failed after {attempt} attempts: {e}"
                    )
                continue

            is_valid, errors = validate_discussion_questions(
                output=output,
                num_questions=inputs.num_questions,
                grade_level=inputs.grade_level,
                teacher_details=inputs.teacher_details,
            )

            if is_valid:
                return {
                    "success": True,
                    "output": output,
                    "attempts": attempt,
                    "errors": [],
                }

            last_errors = errors

            if attempt < self.max_attempts:
                current_prompt = build_repair_prompt(
                    original_prompt=original_prompt,
                    invalid_output=output,
                    validation_errors=errors,
                )

        # All attempts exhausted — return best-effort output
        raise ValueError(
            f"Generation failed after {self.max_attempts} attempts.\n"
            f"Final validation errors:\n"
            + "\n".join(f"  - {e}" for e in last_errors)
            + f"\n\nFinal output:\n{last_output}"
        )


def generate_discussion_questions_from_dict(
    llm_client: LLMClient = None,
    inputs: dict = None,
    max_attempts: int = 3,
    **kwargs,
) -> dict:
    """
    Convenience wrapper: dict → dataclass → generator.
    Accepts both positional llm_client and keyword llm/llm_client.
    """
    if llm_client is None:
        llm_client = kwargs.get("llm") or kwargs.get("llm_client")

    if inputs is None:
        inputs = {}

    discussion_inputs = DiscussionQuestionsInput(
        category=inputs.get("category", inputs.get("subject", "Food Science")),
        topic=inputs.get("topic", ""),
        grade_level=inputs.get(
            "grade_level", inputs.get("gradeLevel", "High")
        ),
        num_questions=5,  # Always 5
        teacher_details=inputs.get(
            "teacher_details", inputs.get("customization", "")
        ),
    )

    generator = DiscussionQuestionsGenerator(
        llm_client=llm_client,
        max_attempts=max_attempts,
    )

    return generator.generate(discussion_inputs)
