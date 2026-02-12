"""
Unit tests for the discussion questions generation system.
"""
from __future__ import annotations
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from apps.generators.discussion_questions.prompt import build_discussion_questions_prompt
from apps.generators.discussion_questions.validation import (
    validate_discussion_questions_output,
    _extract_pairs,
)
from apps.generators.discussion_questions.logic import (
    DiscussionQuestionsInputs,
    LLMClient,
    generate_discussion_questions,
)


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
    prompt = build_discussion_questions_prompt(
        category="Food Safety",
        topic="Bacteria",
        grade_level="High",
        num_questions=3,
        teacher_details="Focus on handwashing"
    )
    
    assert "Food Safety" in prompt
    assert "Bacteria" in prompt
    assert "High" in prompt
    assert "3" in prompt
    assert "Focus on handwashing" in prompt
    assert "GLOBAL FOOD SCIENCE LENS" in prompt


def test_valid_output():
    """Test validation with a valid output."""
    valid_text = """DISCUSSION QUESTIONS

Grade Level: High
Topic: Bacteria

Imagine you're responsible for food safety in a school cafeteria and you notice handwashing has become inconsistent during lunch rush. What clues would you look for to judge whether the risk is increasing, and how confident could you be without lab results?
Teacher cue: Listen for students relying only on smell/appearance; prompt for evidence beyond senses.

Two teams argue about reducing bacterial transfer: Team A wants stricter handwashing, Team B wants gloves and surface sanitation. Which approach would you prioritize first, and what tradeoffs make that decision harder?
Teacher cue: Push for tradeoffs (compliance vs false security, time pressure, cross-contamination routes).

A student says if food looks fine and smells fine it's safe, handwashing matters but it's not that serious. How would you challenge that claim using food science reasoning, and what evidence would you want before making a final judgment?
Teacher cue: Great for surfacing misconceptions; steer toward uncertainty, invisible risk, and limits of sensory checks."""

    errors = validate_discussion_questions_output(
        full_text=valid_text,
        grade_level="High",
        num_questions=3,
        teacher_details=None
    )
    
    assert len(errors) == 0


def test_extract_pairs():
    """Test extracting question-cue pairs."""
    text = """DISCUSSION QUESTIONS

Grade Level: High
Topic: Bacteria

What evidence would you look for to assess food safety risk?
Teacher cue: Listen for misconceptions about visible contamination.

How would you prioritize between handwashing and glove use?
Teacher cue: Push for tradeoffs in decision-making."""

    pairs = _extract_pairs(text)
    assert len(pairs) == 2
    assert pairs[0][0].endswith("?")
    assert pairs[0][1].startswith("Listen for")


def test_invalid_no_question_mark():
    """Test validation catches missing question marks."""
    invalid_text = """DISCUSSION QUESTIONS

Grade Level: High
Topic: Bacteria

What evidence would you look for to assess food safety risk
Teacher cue: Listen for misconceptions."""

    errors = validate_discussion_questions_output(
        full_text=invalid_text,
        grade_level="High",
        num_questions=1,
        teacher_details=None
    )
    
    assert any("question mark" in e.lower() for e in errors)


def test_invalid_recall_question():
    """Test validation catches recall-oriented questions."""
    invalid_text = """DISCUSSION QUESTIONS

Grade Level: High
Topic: Bacteria

What is the definition of cross-contamination in food safety?
Teacher cue: Listen for student responses."""

    errors = validate_discussion_questions_output(
        full_text=invalid_text,
        grade_level="High",
        num_questions=1,
        teacher_details=None
    )
    
    assert any("recall" in e.lower() for e in errors)


def test_generation_with_mock():
    """Test the full generation loop with a mock LLM."""
    valid_response = """DISCUSSION QUESTIONS

Grade Level: High
Topic: Bacteria

What evidence would you rely on to judge whether food handling practices pose an increasing risk, and how confident could you be in that judgment without laboratory testing?
Teacher cue: Listen for over-reliance on appearance; prompt for indirect evidence and context clues.

How would you decide between prioritizing handwashing compliance versus increasing surface sanitation frequency, and what tradeoffs make this decision more complex?
Teacher cue: Push for competing demands (behavior change, resource limits, cross-contamination pathways).

Why might a student's confidence in sensory cues (smell, appearance) create risk in food safety decisions, and what evidence would help challenge that reasoning?
Teacher cue: Surface the misconception that safe-looking food is safe food; steer toward invisible pathogens."""

    mock_llm = MockLLMClient([valid_response])
    
    inputs = DiscussionQuestionsInputs(
        category="Food Safety",
        topic="Bacteria",
        grade_level="High",
        num_questions=3,
        teacher_details=None
    )
    
    result = generate_discussion_questions(
        llm=mock_llm,
        inputs=inputs,
        max_attempts=3
    )
    
    assert result is not None
    assert "DISCUSSION QUESTIONS" in result or "Discussion Questions" in result
    assert mock_llm.call_count == 1


def test_generation_with_repair():
    """Test that the repair loop works when initial output is invalid."""
    invalid_response = """DISCUSSION QUESTIONS

Grade Level: High
Topic: Bacteria

What is bacteria
Teacher cue: Listen for responses."""

    valid_response = """DISCUSSION QUESTIONS

Grade Level: High
Topic: Bacteria

What evidence would you rely on to judge whether food handling practices pose an increasing risk, and how confident could you be in that judgment without laboratory testing?
Teacher cue: Listen for over-reliance on appearance; prompt for indirect evidence and context clues."""

    # First response is invalid, second is valid
    mock_llm = MockLLMClient([invalid_response, valid_response])
    
    inputs = DiscussionQuestionsInputs(
        category="Food Safety",
        topic="Bacteria",
        grade_level="High",
        num_questions=1,
        teacher_details=None
    )
    
    result = generate_discussion_questions(
        llm=mock_llm,
        inputs=inputs,
        max_attempts=3
    )
    
    assert result is not None
    assert mock_llm.call_count == 2  # Should have called twice (initial + repair)


if __name__ == "__main__":
    # Run simple tests
    test_prompt_generation()
    print("✓ Prompt generation test passed")
    
    test_valid_output()
    print("✓ Valid output test passed")
    
    test_extract_pairs()
    print("✓ Extract pairs test passed")
    
    test_invalid_no_question_mark()
    print("✓ Invalid question mark test passed")
    
    test_invalid_recall_question()
    print("✓ Invalid recall question test passed")
    
    test_generation_with_mock()
    print("✓ Generation with mock test passed")
    
    test_generation_with_repair()
    print("✓ Generation with repair test passed")
    
    print("\n✅ All tests passed!")
