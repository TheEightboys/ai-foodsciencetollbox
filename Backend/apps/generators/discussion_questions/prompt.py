"""
Discussion Questions Prompt Builder (v2)
Generates exactly 5 concept-deepening discussion questions
with food science lens, using "Option N" format.
"""


def build_generation_prompt(
    category: str,
    topic: str,
    grade_level: str,
    num_questions: int = 5,
    teacher_details: str = None,
) -> str:
    """
    Build the prompt for generating 5 discussion questions.

    The output uses "Option N" headings (not numbered lists),
    each followed by a single question paragraph and a "Teacher cue:" line.
    """

    grade_language = {
        "Elementary": (
            "Very simple words. Familiar foods and everyday situations (pizza, milk, "
            "leftovers, lunchbox). Short sentences. No jargon. "
            "Focus on everyday choices and simple cause/effect."
        ),
        "Middle": (
            "Some basic scientific words are okay but keep it simple. "
            "Clear cause/effect. Concrete food examples. "
            "Focus on safe choices and reasoning without heavy terms."
        ),
        "High": (
            "More precise language. Strong focus on evidence, decision-making, "
            "and tradeoffs. Can handle more abstract reasoning but avoid jargon overload."
        ),
        "College": (
            "Professional tone but still discussion-friendly. "
            "Systems thinking and tradeoffs. Still readable, not dense, not a lecture."
        ),
    }

    language_guide = grade_language.get(grade_level, grade_language["High"])

    # --- Teacher details block ---
    teacher_block = ""
    teacher_requirement = ""
    if teacher_details:
        teacher_block = f"""

TEACHER CONTEXT (HIGHEST PRIORITY):
{teacher_details}"""
        teacher_requirement = (
            "\n- At least 2 of the 5 questions MUST clearly incorporate the teacher context above."
        )

    prompt = f"""You are a food-science curriculum specialist creating concept-deepening discussion questions.

FOOD SCIENCE LENS (NON-NEGOTIABLE):
Every question must be grounded in real food situations — kitchen, cafeteria, food handling,
storage, sanitation, spoilage, food safety, quality, shelf life, cross-contamination, or risk.
Never write generic science questions. Never use clinical/medical framing unless directly tied
to foodborne illness risk in foods.

INPUTS:
Category: {category}
Topic: {topic}
Grade Level: {grade_level}{teacher_block}

LANGUAGE LEVEL for {grade_level}:
{language_guide}

━━━ EXACT OUTPUT FORMAT ━━━
Return ONLY the following. No extra commentary, analysis, or system notes.

Discussion Questions

Grade Level: {grade_level}
Topic: {topic}


Option 1
<Question written as a full paragraph ending with a question mark>
Teacher cue: <one concise sentence>

Option 2
<Question written as a full paragraph ending with a question mark>
Teacher cue: <one concise sentence>

Option 3
<Question written as a full paragraph ending with a question mark>
Teacher cue: <one concise sentence>

Option 4
<Question written as a full paragraph ending with a question mark>
Teacher cue: <one concise sentence>

Option 5
<Question written as a full paragraph ending with a question mark>
Teacher cue: <one concise sentence>

━━━ FORMAT RULES ━━━
- Do NOT use "1." "2." etc. — only use "Option 1" through "Option 5" on their own lines
- Do NOT place numbering in front of the question itself
- No bullet points
- No markdown (no **, no ##, no bold markers)
- No quotation marks
- Each Option block must include exactly one question and exactly one "Teacher cue:" line
- Each question must end with a question mark
- Each Teacher cue line must begin with "Teacher cue:"
- No extra text before "Discussion Questions" or after the last Teacher cue

━━━ QUESTION QUALITY RULES (hard requirements) ━━━
Each question must:
- Be open-ended (NOT yes/no)
- Be discussion-rich (supports ~5 minutes)
- Be reasoning-based (not definitions, listing, or recall)
- Include at least one discussion move: evidence/clues, tradeoffs, risk, confidence/uncertainty, deciding and justifying
- Avoid numeric thresholds (no temps, times, ppm, etc.) — reject ALL digits
- Start with How / Why / What / When / Which
- Clearly include food context (kitchen/cafeteria/handling/storage/sanitation/spoilage/quality/shelf life/cross-contamination)

Variety rules across the 5:
- No more than 2 questions can start with the same first word
- Use a mix of question types:
  * scenario decision
  * compare / tradeoff
  * critique a claim / challenge a misconception
  * propose a strategy
  * investigate what went wrong and judge confidence{teacher_requirement}

━━━ TEACHER CUE RULES ━━━
Every Teacher cue must:
- Be one sentence
- Start with one of: "Listen for" / "Push for" / "Prompt for" / "If students stall"
- Be teacher-facing facilitation help (not content teaching)
- Help deepen the discussion (misconception, evidence, tradeoffs, what to listen for)

━━━ TONE ━━━
- No scare language (no "deadly/fatal/you could die")
- No moralizing absolutes
- Professional, curious, food-science focused

Generate the 5 discussion questions now following ALL rules exactly.""".strip()

    return prompt


def build_repair_prompt(
    original_prompt: str,
    invalid_output: str,
    validation_errors: list,
) -> str:
    """Build repair prompt for fixing invalid output."""

    errors_formatted = "\n".join(f"- {error}" for error in validation_errors)

    return f"""The previous output did not meet the strict requirements.
Fix ALL errors listed below and return ONLY the corrected output.

ORIGINAL PROMPT:
{original_prompt}

PREVIOUS OUTPUT (INVALID):
{invalid_output}

VALIDATION ERRORS:
{errors_formatted}

Return ONLY the corrected discussion questions output following the exact format and ALL rules. No explanations, no apologies."""