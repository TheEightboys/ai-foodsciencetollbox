"""
Unit tests for the learning objectives generation system.
"""
from __future__ import annotations
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from apps.generators.learning_objectives.prompt import (
    build_learning_objectives_prompt,
    FORBIDDEN_VERBS,
    ALLOWED_START_VERBS,
)
from apps.generators.learning_objectives.validation import (
    validate_learning_objectives_output,
    _contains_forbidden_verbs,
    _extract_objective_lines,
    _objective_start_verb,
    _check_verb_diversity,
)
from apps.generators.learning_objectives.logic import GenerationInputs, LLMClient, generate_learning_objectives


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_count = 0
    
    def generate_text(self, prompt: str) -> str:
        if self.call_count >= len(self.responses):
            return self.responses[-1]
        response = self.responses[self.call_count]
        self.call_count += 1
        return response


def test_prompt_generation():
    """Test that prompt is generated correctly."""
    prompt = build_learning_objectives_prompt(
        category="Food Safety",
        topic="Pasteurization",
        grade_level="High",
        teacher_details="Focus on dairy processing"
    )
    
    assert "Food Safety" in prompt
    assert "Pasteurization" in prompt
    assert "High" in prompt
    assert "Focus on dairy processing" in prompt
    assert "FOOD SCIENTIST LENS" in prompt


def test_forbidden_verbs_detection():
    """Test that forbidden verbs are detected."""
    text = "Students will learn about food safety and understand pasteurization."
    hits = _contains_forbidden_verbs(text)
    
    assert "learn" in hits
    assert "understand" in hits


def test_valid_output():
    """Test validation with a valid output."""
    valid_text = """LESSON OBJECTIVES

Grade Level: High School
Topic: Pasteurization

By the end of this lesson, students will be able to:
1. Explain the scientific principles behind pasteurization processes.
2. Analyze the impact of temperature and time on microbial reduction.
3. Evaluate different pasteurization methods for various food products.
4. Apply pasteurization knowledge to ensure food safety.
5. Assess the quality impacts of thermal processing on dairy products."""

    result, errors = validate_learning_objectives_output(
        raw_text=valid_text,
        grade_level="High",
        topic="Pasteurization",
        teacher_details=None
    )
    
    assert result is not None
    assert len(errors) == 0
    assert len(result.objectives) == 5
    assert result.grade_level == "High"
    assert result.topic == "Pasteurization"


def test_invalid_output_too_few_objectives():
    """Test validation with too few objectives."""
    invalid_text = """LESSON OBJECTIVES

Grade Level: High School
Topic: Pasteurization

By the end of this lesson, students will be able to:
1. Explain the scientific principles behind pasteurization.
2. Analyze the impact of temperature on microbial reduction."""

    result, errors = validate_learning_objectives_output(
        raw_text=invalid_text,
        grade_level="High",
        topic="Pasteurization",
        teacher_details=None
    )
    
    assert result is None
    assert len(errors) > 0
    assert any("4–6" in error for error in errors)


def test_verb_diversity():
    """Test verb diversity checking."""
    objectives = [
        "Explain the concept of pasteurization.",
        "Explain the temperature requirements.",
        "Explain the time duration needed.",
    ]
    
    error = _check_verb_diversity(objectives)
    assert error is not None
    assert "Explain" in error


def test_objective_start_verb_extraction():
    """Test extracting the starting verb from an objective."""
    obj = "Explain the scientific principles behind pasteurization."
    verb = _objective_start_verb(obj)
    assert verb == "Explain"


def test_generation_with_mock():
    """Test the full generation loop with a mock LLM."""
    valid_response = """LESSON OBJECTIVES

Grade Level: High
Topic: Pasteurization

By the end of this lesson, students will be able to:
1. Explain the scientific principles behind pasteurization processes.
2. Analyze the impact of temperature and time on microbial reduction.
3. Evaluate different pasteurization methods for various food products.
4. Apply pasteurization knowledge to ensure food safety.
5. Assess the quality impacts of thermal processing on dairy products."""

    mock_llm = MockLLMClient([valid_response])
    
    inputs = GenerationInputs(
        category="Food Safety",
        topic="Pasteurization",
        grade_level="High",
        teacher_details=None
    )
    
    result = generate_learning_objectives(
        llm=mock_llm,
        inputs=inputs,
        max_attempts=3
    )
    
    assert result is not None
    assert len(result.objectives) == 5
    assert mock_llm.call_count == 1


def test_generation_with_repair():
    """Test that the repair loop works when initial output is invalid."""
    invalid_response = """LESSON OBJECTIVES

Grade Level: High
Topic: Pasteurization

By the end of this lesson, students will be able to:
1. Learn about pasteurization.
2. Understand food safety."""

    valid_response = """LESSON OBJECTIVES

Grade Level: High
Topic: Pasteurization

By the end of this lesson, students will be able to:
1. Explain the scientific principles behind pasteurization processes.
2. Analyze the impact of temperature and time on microbial reduction.
3. Evaluate different pasteurization methods for various food products.
4. Apply pasteurization knowledge to ensure food safety.
5. Assess the quality impacts of thermal processing on dairy products."""

    # First response is invalid, second is valid
    mock_llm = MockLLMClient([invalid_response, valid_response])
    
    inputs = GenerationInputs(
        category="Food Safety",
        topic="Pasteurization",
        grade_level="High",
        teacher_details=None
    )
    
    result = generate_learning_objectives(
        llm=mock_llm,
        inputs=inputs,
        max_attempts=3
    )
    
    assert result is not None
    assert len(result.objectives) == 5
    assert mock_llm.call_count == 2  # Should have called twice (initial + repair)


if __name__ == "__main__":
    # Run simple tests
    test_prompt_generation()
    print("✓ Prompt generation test passed")
    
    test_forbidden_verbs_detection()
    print("✓ Forbidden verbs detection test passed")
    
    test_valid_output()
    print("✓ Valid output test passed")
    
    test_invalid_output_too_few_objectives()
    print("✓ Invalid output test passed")
    
    test_verb_diversity()
    print("✓ Verb diversity test passed")
    
    test_objective_start_verb_extraction()
    print("✓ Verb extraction test passed")
    
    test_generation_with_mock()
    print("✓ Generation with mock test passed")
    
    test_generation_with_repair()
    print("✓ Generation with repair test passed")
    
    print("\n✅ All tests passed!")
