# generators/lesson_starter/prompt.py
"""
Prompt builder for the Lesson Starter Ideas generator (v2).

The new format produces exactly 7 varied, practical, 5-minute lesson starter
ideas — idea generation, not scripted teaching.
"""
from __future__ import annotations


# ── Grade-level pedagogy guidance ──────────────────────────────────────────────
GRADE_LEVEL_GUIDANCE = {
    "Elementary": """
ELEMENTARY LEVEL RULES:
- Use concrete, simple language and familiar foods (pizza, milk, bread, fruit, lunch)
- Simple questions: yes/no predictions, show-and-tell, quick observation
- No technical or scientific vocabulary
- Focus on observation and basic reasoning
- Short, clear prompts a young student can immediately understand
- Examples of appropriate hooks: "Is this apple still good to eat?", ranking lunch items by freshness
""",
    "Middle": """
MIDDLE SCHOOL LEVEL RULES:
- Use some scientific vocabulary with everyday food examples
- Light reasoning: quick ranking/prediction, simple misconceptions, short partner talk
- Surface-level misconceptions are appropriate
- Prompts can involve basic comparison or classification
- Examples of appropriate hooks: ranking foods by spoilage risk, myth-checking common beliefs about leftovers
""",
    "High": """
HIGH SCHOOL LEVEL RULES:
- More precise language emphasizing decision-making under uncertainty
- Judgment calls involving risk, evidence, and tradeoffs
- Real-world food handling decisions and industry context
- Still not jargon-heavy — accessible but mature
- Examples of appropriate hooks: evaluating whether a food recall is justified, deciding if a restaurant passes inspection based on clues
""",
    "College": """
COLLEGE LEVEL RULES:
- Professional tone with systems thinking and risk analysis
- Judgment calls, policy implications, process decisions
- Can reference supply chain, regulatory frameworks, HACCP concepts at a high level
- Still practical and completable in 5 minutes — no extended case studies
- Examples of appropriate hooks: weighing a product hold/release decision, debating a policy tradeoff in a processing facility
""",
}


def build_lesson_starter_prompt(
    *,
    category: str,
    topic: str,
    grade_level: str,
    teacher_details: str | None = None,
    time_needed: str | None = None,   # ignored — always 5 min
) -> str:
    """
    Build the prompt for generating 7 lesson starter ideas.

    Parameters
    ----------
    category : str
        Subject area (e.g. "Science"). Used internally.
    topic : str
        The specific food-science topic for the lesson.
    grade_level : str
        One of Elementary, Middle, High, College.
    teacher_details : str | None
        Optional teacher context — highest priority if provided.
    time_needed : str | None
        IGNORED. All starters are 5 minutes by design.

    Returns
    -------
    str
        The complete prompt for the LLM.
    """
    grade_guidance = GRADE_LEVEL_GUIDANCE.get(
        grade_level, GRADE_LEVEL_GUIDANCE["High"]
    )

    teacher_block = ""
    if teacher_details and teacher_details.strip():
        teacher_block = f"""
TEACHER CONTEXT (HIGHEST PRIORITY):
{teacher_details.strip()}
- At least 2 of the 7 ideas should reflect or incorporate this context.
"""

    return f"""You are an expert food scientist and curriculum designer.

TASK:
Generate exactly 7 different lesson starter ideas for a food science class.
Every idea must be a quick, practical, 5-minute hook — NOT a mini lesson.

CONTEXT:
- Topic: {topic}
- Grade Level: {grade_level}
{teacher_block}

─── FOOD SCIENCE LENS (NON-NEGOTIABLE) ───
All 7 ideas MUST stay within a food science context.
Even if the topic touches biology, chemistry, or microbiology, every idea must
connect to: food safety, food handling, storage, preparation, quality, shelf life,
risk decisions, or real-world food systems.
Do NOT drift into generic science teaching.

─── GRADE-LEVEL DIFFERENTIATION (CRITICAL) ───
{grade_guidance}
You must adjust vocabulary, complexity, type of thinking, and depth of reasoning
to match the selected grade level. The ideas must FEEL appropriate for that level.

─── 5-MINUTE IMPLEMENTATION RULE ───
Every idea must be clearly doable in 5 minutes. That means:
- No long writing assignments
- No labs or experiments
- No extended reading passages
- No full debates requiring preparation
- No complex group restructuring
Each idea must be something a teacher can:
  say, write on the board, show a quick image, pose as a prompt,
  or run as a quick ranking/prediction activity.
If an idea would realistically take more than 5 minutes, do NOT include it.

─── IDEA DIFFERENTIATION REQUIREMENT ───
The 7 ideas must NOT be repetitive. They must represent different types of hooks.
Use a MIX of these styles (at least 5 different styles across the 7 ideas):
  - Scenario-based prompt
  - Prediction activity
  - Ranking activity
  - Myth check / true-or-false hook
  - Debate-style quick prompt
  - Real-world case or news hook
  - Creative design prompt
  - Comparison activity
  - Quick survey / show of hands
  - "Would you eat this?" challenge

─── EXACT OUTPUT FORMAT ───
Return ONLY the following. No extra commentary, analysis, or system notes.

Lesson Starter Ideas

Grade Level: {grade_level}
Topic: {topic}

Option 1: [Short Title]
[3-5 sentence description explaining: the scenario/prompt/activity, what students will do, and why it works as a hook]

Option 2: [Short Title]
[3-5 sentence description]

Option 3: [Short Title]
[3-5 sentence description]

Option 4: [Short Title]
[3-5 sentence description]

Option 5: [Short Title]
[3-5 sentence description]

Option 6: [Short Title]
[3-5 sentence description]

Option 7: [Short Title]
[3-5 sentence description]

─── FORMAT RULES ───
- Do NOT use markdown (no **, no ##, no bullets)
- Each idea title line must start with "Option N: " (e.g. "Option 1: The Invisible Threat Scenario")
- Each description must be exactly 3-5 sentences
- No scripts, no word count pressure, no strict formatting beyond this structure
- No extra commentary before or after the 7 ideas
- This is idea generation, not scripted teaching

Generate the 7 lesson starter ideas now following ALL rules exactly.""".strip()


def build_repair_prompt(
    original_prompt: str,
    invalid_output: str,
    validation_errors: list,
) -> str:
    """
    Build a repair prompt when validation fails.
    """
    errors_formatted = "\n".join(f"- {error}" for error in validation_errors)

    return f"""The previous output did not meet the requirements. Fix ALL errors and return ONLY the corrected output with NO commentary.

ORIGINAL PROMPT:
{original_prompt}

PREVIOUS OUTPUT (INVALID):
{invalid_output}

VALIDATION ERRORS:
{errors_formatted}

Return ONLY the corrected lesson starter ideas output following the exact format and ALL rules. No explanations, no apologies."""


# Keep legacy alias for backward compatibility
def build_generation_prompt(
    category: str,
    topic: str,
    grade_level: str,
    time_needed: str = "5 minutes",
    teacher_details: str = None,
) -> str:
    """Legacy alias — delegates to build_lesson_starter_prompt."""
    return build_lesson_starter_prompt(
        category=category,
        topic=topic,
        grade_level=grade_level,
        teacher_details=teacher_details,
    )
