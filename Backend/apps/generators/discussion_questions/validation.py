"""
Discussion Questions Validation (v2)
Validates output against the "Option N" format with 5 questions.

Checks:
- Starts with "Discussion Questions"
- Contains Grade Level and Topic lines
- Contains exactly 5 option blocks
- Each option has an Option line, one question ending in "?", one "Teacher cue:" line
- Teacher cue starts with Listen for / Push for / Prompt for / If students stall
- Question starts with How/Why/What/When/Which
- No recall wording (define, list, name, etc.)
- No numeric facts in the question
- Clear food context in each question
- Variety rule on first words
- If teacher_details exist: at least 2 questions reflect it
"""

import re
from typing import List, Tuple, Optional
from collections import Counter


def validate_discussion_questions(
    output: str,
    num_questions: int = 5,
    grade_level: str = "High",
    teacher_details: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """
    Validate discussion questions output against all constraints.
    Returns (is_valid, errors).
    """
    if output is None:
        output = ""
    elif not isinstance(output, str):
        output = str(output)

    if teacher_details is None:
        teacher_details = ""
    elif not isinstance(teacher_details, str):
        teacher_details = str(teacher_details)

    errors: list[str] = []
    t = output.strip()

    # ── 1. Check header ──────────────────────────────────────
    if "Discussion Questions" not in t and "discussion questions" not in t.lower():
        errors.append("Missing required header: 'Discussion Questions'")

    if "Grade Level:" not in t:
        errors.append("Missing required line: 'Grade Level:'")

    if "Topic:" not in t:
        errors.append("Missing required line: 'Topic:'")

    # ── 2. Extract option blocks ─────────────────────────────
    pairs = _extract_option_blocks(output)

    if len(pairs) != num_questions:
        errors.append(
            f"Expected exactly {num_questions} option blocks, found {len(pairs)}"
        )

    # ── 3. Per-option checks ─────────────────────────────────
    for idx, block in enumerate(pairs, 1):
        q = block["question"]
        cue = block["cue"]

        # --- Question checks ---
        if not q:
            errors.append(f"Option {idx}: missing question text.")
            continue

        if not q.strip().endswith("?"):
            errors.append(f"Option {idx}: question does not end with '?'")

        # Must start with How/Why/What/When/Which
        starters = ("How", "Why", "What", "When", "Which")
        if not q.lstrip().startswith(starters):
            errors.append(
                f"Option {idx}: question must start with How/Why/What/When/Which"
            )

        # No recall wording
        recall_patterns = [
            r"\bdefine\b", r"\blist\b", r"\bname\b",
            r"\bidentify the\b", r"\bwhat is the definition\b",
            r"\bwhat does .* mean\b",
        ]
        q_lower = q.lower()
        for pat in recall_patterns:
            if re.search(pat, q_lower):
                errors.append(
                    f"Option {idx}: question uses recall wording (not allowed)"
                )
                break

        # No digits
        if re.search(r"\d", q):
            errors.append(
                f"Option {idx}: question contains numeric digits (not allowed)"
            )

        # Discussion cues — broad set of reasoning/analysis vocabulary
        discussion_cues = [
            "evidence", "clues", "confidence", "decide", "tradeoff",
            "tradeoffs", "trade-off", "trade-offs", "risk", "uncertain",
            "uncertainty", "justify", "defend", "prioritize", "compare",
            "weigh", "evaluate", "assess", "judgment", "implications",
            "impact", "factors", "consequences", "considerations",
            "inform", "influence", "mitigate", "balance", "prevent",
            "enhance", "affect", "contribute", "determine", "reason",
            "reasoning", "cause", "effect", "relationship", "connection",
            "differ", "different", "difference", "change", "improve",
            "reduce", "increase", "advantage", "disadvantage", "benefit",
            "concern", "challenge", "strategy", "approach", "decision",
            "might", "could", "should", "would", "explain", "support",
        ]
        if not any(cue_word in q_lower for cue_word in discussion_cues):
            errors.append(
                f"Option {idx}: missing discussion cue "
                "(evidence/tradeoff/risk/confidence/etc.)"
            )

        # Food context
        food_contexts = [
            "kitchen", "cafeteria", "leftover", "fridge", "refrigerator",
            "milk", "meat", "produce", "storage", "store", "sanitation",
            "cross-contamination", "shelf life", "spoil", "quality",
            "preparation", "prepare", "handling", "handle", "safety",
            "safe", "food", "cook", "raw", "fresh", "frozen", "thaw",
            "refrigerate",
        ]
        if not any(ctx in q_lower for ctx in food_contexts):
            errors.append(
                f"Option {idx}: missing clear food context"
            )

        # Yes/no check
        yes_no = [
            r"^Is ", r"^Are ", r"^Do ", r"^Does ", r"^Can ",
            r"^Could ", r"^Should ", r"^Would ", r"^Will ",
            r"^Has ", r"^Have ",
        ]
        if any(re.match(p, q.strip(), re.IGNORECASE) for p in yes_no):
            errors.append(
                f"Option {idx}: appears to be yes/no (must be open-ended)"
            )

        # --- Teacher cue checks ---
        if not cue:
            errors.append(f"Option {idx}: missing Teacher cue line.")
            continue

        required_starts = (
            "Listen for", "Push for", "Prompt for", "If students stall",
        )
        if not cue.startswith(required_starts):
            errors.append(
                f"Option {idx}: Teacher cue must start with "
                "'Listen for'/'Push for'/'Prompt for'/'If students stall'"
            )

        # One sentence check (rough: ≤ 30 words)
        if len(cue.split()) > 30:
            errors.append(
                f"Option {idx}: Teacher cue too long — keep to one concise sentence"
            )

    # ── 4. Variety check ─────────────────────────────────────
    if len(pairs) >= 2:
        first_words: list[str] = []
        for block in pairs:
            q = block["question"]
            if q:
                m = re.match(r"^(\w+)", q.strip())
                if m:
                    first_words.append(m.group(1))
        counts = Counter(first_words)
        for word, cnt in counts.items():
            if cnt > 2:
                errors.append(
                    f"Too many questions ({cnt}) start with '{word}' (max 2)"
                )

    # ── 5. Teacher details incorporation ─────────────────────
    if teacher_details.strip() and len(pairs) > 0:
        keywords = _extract_keywords(teacher_details)
        if keywords:
            inc = 0
            for block in pairs:
                combined = (block["question"] + " " + block["cue"]).lower()
                if any(kw in combined for kw in keywords):
                    inc += 1
            if inc < 2:
                errors.append(
                    f"Teacher context not sufficiently incorporated: "
                    f"need at least 2 questions to reflect it, found {inc}"
                )

    return (len(errors) == 0, errors)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _extract_option_blocks(output: str) -> List[dict]:
    """
    Parse "Option N" blocks from the output.
    Returns list of dicts: { "number": int, "question": str, "cue": str }
    """
    if not output:
        return []

    blocks: list[dict] = []

    # Split on "Option N" lines
    pattern = re.compile(
        r"Option\s+(\d+)\s*\n(.+?)(?=Option\s+\d+\s*\n|\Z)",
        re.DOTALL | re.IGNORECASE,
    )

    for match in pattern.finditer(output):
        number = int(match.group(1))
        body = match.group(2).strip()

        question = ""
        cue = ""

        # Find the Teacher cue line
        cue_match = re.search(
            r"Teacher\s+cue:\s*(.+)", body, re.IGNORECASE,
        )
        if cue_match:
            cue = cue_match.group(1).strip()
            # Everything before the cue line is the question
            question = body[: cue_match.start()].strip()
        else:
            question = body

        blocks.append({
            "number": number,
            "question": question,
            "cue": cue,
        })

    return blocks


def _extract_keywords(teacher_details: str) -> List[str]:
    """Extract meaningful keywords from teacher details."""
    if not teacher_details:
        return []

    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "as", "is", "was", "are",
        "were", "be", "been", "being", "have", "has", "had", "do",
        "does", "did", "will", "would", "should", "could", "may",
        "might", "must", "can", "this", "that", "these", "those",
        "i", "you", "he", "she", "it", "we", "they",
    }

    words = re.findall(r"\b\w+\b", teacher_details.lower())
    keywords = [w for w in words if len(w) >= 3 and w not in stop_words]

    seen: set[str] = set()
    unique: list[str] = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
            if len(unique) >= 20:
                break

    return unique