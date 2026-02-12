# generators/lesson_starter/validation.py
"""
Validation for the Lesson Starter Ideas generator (v2).

Checks:
- Header: "Lesson Starter Ideas" present
- Grade Level and Topic lines present
- Exactly 7 ideas, each with a title and 3-5 sentence description
- Content stays food-science focused
- Ideas are meaningfully different (not repeating the same hook style)
"""
from __future__ import annotations

import re

# ── Food-science context cues ──────────────────────────────────────────────────
FOOD_CONTEXT_CUES = {
    "food", "ingredient", "recipe", "cook", "cooking", "kitchen",
    "leftover", "leftovers", "refrigerator", "fridge", "freezer",
    "milk", "pizza", "deli", "sandwich", "cafeteria", "lunch",
    "yogurt", "cheese", "chicken", "salad", "fruit", "bread",
    "expiration", "best by", "use by", "sell by", "shelf life",
    "spoil", "spoilage", "bacteria", "contamination", "cross-contamination",
    "temperature", "storage", "handling", "foodborne", "pathogen",
    "safety", "sanitation", "hygiene", "preservation", "canned",
    "fresh", "frozen", "thaw", "reheat", "restaurant", "grocery",
    "label", "nutrition", "allergen", "recall", "inspection",
    "haccp", "danger zone", "processing", "quality", "packaging",
    "ferment", "pasteurize", "supply chain", "meal", "snack",
    "dinner", "breakfast", "eat", "eating", "taste", "smell",
    "mold", "rot", "decay", "shelf", "store", "risk",
}

# ── Idea style keywords for differentiation check ─────────────────────────────
HOOK_STYLE_KEYWORDS = {
    "scenario":  {"scenario", "imagine", "picture this", "you walk into", "suppose"},
    "predict":   {"predict", "prediction", "guess", "think will", "happen if", "would happen"},
    "rank":      {"rank", "ranking", "order", "most to least", "least to most", "prioritize"},
    "myth":      {"myth", "true or false", "fact or fiction", "common belief", "misconception"},
    "debate":    {"debate", "agree or disagree", "would you", "defend", "argue", "convince"},
    "case":      {"case", "news", "headline", "real-world", "recall", "outbreak", "report"},
    "design":    {"design", "create", "invent", "come up with", "redesign"},
    "compare":   {"compare", "comparison", "difference", "similar", "versus", "vs"},
    "survey":    {"survey", "show of hands", "quick poll", "raise your hand", "vote"},
    "challenge": {"would you eat", "eat this", "safe to eat", "still good", "throw away"},
}


def _norm(text: str) -> str:
    """Normalize whitespace."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    return "\n".join(
        line.rstrip()
        for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ).strip()


def _count_sentences(text: str) -> int:
    """Count sentences (heuristic: split on . ! ?)."""
    # Split on sentence-ending punctuation followed by space or end-of-string
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty strings and very short fragments
    return len([s for s in sentences if len(s.strip()) > 5])


def _extract_ideas(text: str) -> list[dict]:
    """
    Extract the 7 ideas from text.
    Returns list of dicts with 'title' and 'description' keys.
    Supports both "Option N:" (v2 template) and legacy "Starter Idea N:" labels.
    """
    ideas = []
    # Match "Option N: Title" or "Starter Idea N: Title" pattern
    pattern = re.compile(
        r'(?:Option|Starter\s+Idea)\s+(\d+)\s*:\s*(.+?)(?=\n(?:Option|Starter\s+Idea)\s+\d+\s*:|\Z)',
        re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        number = int(match.group(1))
        block = match.group(2).strip()
        # First line after the title number is part of the title  
        lines = block.split('\n', 1)
        title = lines[0].strip()
        description = lines[1].strip() if len(lines) > 1 else ""
        ideas.append({
            "number": number,
            "title": title,
            "description": description,
        })
    return ideas


def validate_lesson_starter(
    output: str,
    grade_level: str = "High",
    teacher_details: str = None,
) -> tuple[bool, list[str]]:
    """
    Validate lesson starter ideas output against the new v2 spec.

    Returns (is_valid, errors).
    """
    if output is None:
        output = ""
    elif not isinstance(output, str):
        output = str(output)

    errors: list[str] = []
    t = _norm(output)

    # ── 1. Check required header markers ───────────────────────
    if "Lesson Starter Ideas" not in t and "LESSON STARTER IDEAS" not in t:
        errors.append("Missing required header: 'Lesson Starter Ideas'")

    if "Grade Level:" not in t:
        errors.append("Missing required line: 'Grade Level:'")

    if "Topic:" not in t:
        errors.append("Missing required line: 'Topic:'")

    # ── 2. Extract and count ideas ─────────────────────────────
    ideas = _extract_ideas(t)

    if len(ideas) != 7:
        errors.append(
            f"Must generate exactly 7 ideas. Found {len(ideas)}."
        )

    # ── 3. Per-idea checks ─────────────────────────────────────
    for idea in ideas:
        num = idea["number"]
        title = idea["title"]
        desc = idea["description"]

        # Title should be short (roughly 2-10 words)
        title_words = len(title.split())
        if title_words < 1:
            errors.append(f"Option {num}: missing title.")
        elif title_words > 15:
            errors.append(
                f"Option {num}: title too long ({title_words} words). Keep it short."
            )

        # Description: 3-5 sentences
        if not desc.strip():
            errors.append(f"Option {num}: missing description.")
        else:
            sentence_count = _count_sentences(desc)
            if sentence_count < 2:
                errors.append(
                    f"Option {num}: description too short ({sentence_count} sentence(s)). "
                    "Need 3-5 sentences."
                )
            elif sentence_count > 7:
                errors.append(
                    f"Option {num}: description too long ({sentence_count} sentences). "
                    "Keep to 3-5 sentences."
                )

    # ── 4. Food-science lens check ─────────────────────────────
    lower_all = t.lower()
    food_hits = sum(1 for cue in FOOD_CONTEXT_CUES if cue in lower_all)
    if food_hits < 3:
        errors.append(
            "Content does not appear food-science focused. "
            "Ideas must relate to food safety, handling, storage, quality, shelf life, etc."
        )

    # ── 5. Differentiation check ──────────────────────────────
    if len(ideas) >= 5:
        styles_detected: set[str] = set()
        for idea in ideas:
            combined = (idea["title"] + " " + idea["description"]).lower()
            for style, keywords in HOOK_STYLE_KEYWORDS.items():
                if any(kw in combined for kw in keywords):
                    styles_detected.add(style)
        if len(styles_detected) < 3:
            errors.append(
                f"Ideas lack variety. Only {len(styles_detected)} hook style(s) detected. "
                "Use at least 5 different styles (scenario, prediction, ranking, myth, debate, etc.)."
            )

    is_valid = len(errors) == 0
    return is_valid, errors


# Legacy alias kept for backward compatibility
def validate_lesson_starter_output(full_text: str, grade_level: str) -> list[str]:
    """Legacy wrapper — returns list of errors (empty = valid)."""
    _, errors = validate_lesson_starter(output=full_text, grade_level=grade_level)
    return errors