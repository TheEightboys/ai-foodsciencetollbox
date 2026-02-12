"""
Learning Objectives Prompt Builder - FINAL CONSOLIDATED VERSION
Combines: Accuracy-first approach + Grade differentiation + Performance optimization

This is the definitive version that incorporates:
1. Domain routing (accuracy-first)
2. Improved grade-level differentiation
3. Performance optimizations
"""

from typing import Dict


def build_generation_prompt_final(
    user_intent: str,
    grade_level: str,
    routing_result: Dict,
    num_objectives: int = 5
) -> str:
    """
    Build final consolidated prompt with all improvements.
    
    Args:
        user_intent: Natural language description of learning goal
        grade_level: Elementary, Middle, High, or College
        routing_result: Output from domain_routing.route_to_domain()
        num_objectives: Target number (4-10, default 5)
    
    Returns:
        Optimized prompt for fast, accurate generation
    """
    
    domain = routing_result['domain']
    apply_food_overlay = routing_result['apply_food_overlay']
    domain_description = routing_result['domain_description']
    
    # IMPROVED: More distinct verb lists with minimal overlap (from differentiation update)
    grade_verbs = {
        'Elementary': [
            'Identify', 'Describe', 'Demonstrate', 'Compare', 'Classify',
            'List', 'Name', 'Show', 'Label', 'Sort', 'Match', 'Illustrate',
            'Apply', 'Predict'
        ],
        'Middle': [
            'Explain', 'Compare', 'Contrast', 'Categorize', 'Organize',
            'Distinguish', 'Examine', 'Investigate', 'Determine', 'Calculate',
            'Relate', 'Summarize'
        ],
        'High': [
            'Analyze', 'Evaluate', 'Justify', 'Assess', 'Propose',
            'Design', 'Develop', 'Interpret', 'Predict', 'Critique',
            'Construct', 'Test'
        ],
        'College': [
            'Synthesize', 'Formulate', 'Optimize', 'Validate', 'Defend',
            'Hypothesize', 'Model', 'Theorize', 'Integrate', 'Devise',
            'Appraise', 'Engineer'
        ]
    }
    
    # IMPROVED: Stronger forbidden verbs (from differentiation update)
    grade_forbidden = {
        'Elementary': [
            'Analyze', 'Evaluate', 'Critique', 'Synthesize', 'Formulate',
            'Optimize', 'Defend', 'Validate', 'Assess', 'Justify',
            'Interpret', 'Design', 'Develop', 'Explain', 'Investigate',
            'Hypothesize', 'Model', 'Theorize'
        ],
        'Middle': [
            'Critique', 'Synthesize', 'Formulate', 'Optimize', 'Defend',
            'Validate', 'Hypothesize', 'Model', 'Theorize',
            'Analyze', 'Evaluate', 'Assess', 'Justify'
        ],
        'High': [
            'Synthesize', 'Formulate', 'Optimize', 'Validate',
            'Hypothesize', 'Model', 'Theorize', 'Integrate', 'Devise',
            'Engineer'
        ],
        'College': [
            'Match', 'Label', 'Sort', 'List', 'Name', 'Identify', 'Show'
        ]
    }
    
    # IMPROVED: Enhanced contextual complexity guidance (from differentiation update)
    grade_context = {
        'Elementary': """
COMPLEXITY LEVEL: Basic, concrete understanding with direct instruction

Expectations:
- Students identify and describe observable phenomena
- Focus on what students can see, touch, or directly experience
- Simple cause-and-effect relationships (1-2 variables)
- Guided practice with clear teacher modeling
- Familiar, everyday contexts (home, school, playground)
- Concrete examples, no abstract concepts

Independence: High teacher support and scaffolding
Sources: 1-2 sources (textbook, teacher demonstration)
Time Frame: Single class period activities
Product: Simple demonstrations, basic worksheets, concrete examples
""",
        
        'Middle': """
COMPLEXITY LEVEL: Conceptual understanding with structured frameworks

Expectations:
- Students explain processes and relationships between concepts
- Focus on WHY things happen and HOW they work
- Compare 2-4 approaches using teacher-provided criteria
- Work with structured frameworks and guiding questions
- Handle multi-factor situations (3-4 variables) with some independence
- Developing abstract thinking, using models and diagrams

Independence: Moderate support with structured frameworks
Sources: 2-4 provided sources with guiding questions
Time Frame: Multiple class periods or short projects (1-2 weeks)
Product: Organized reports, comparison charts, structured investigations
""",
        
        'High': """
COMPLEXITY LEVEL: Analysis and application with significant independence

Expectations:
- Students independently analyze complex, multi-variable scenarios
- Evaluate situations and justify decisions using evidence
- Design solutions to authentic, real-world problems
- Work with minimal scaffolding or teacher support
- Handle conflicting information and make trade-off decisions
- Apply knowledge to novel situations not directly taught

Independence: Minimal scaffolding, student-driven inquiry
Sources: 4-6 sources, students find some independently
Time Frame: Extended projects and investigations (2-4 weeks)
Product: Research papers, original designs, evidence-based arguments
""",
        
        'College': """
COMPLEXITY LEVEL: Synthesis and professional-level critical thinking

Expectations:
- Students synthesize information from multiple primary sources
- Create new frameworks, comprehensive plans, or theoretical models
- Critique existing practices using current research and theory
- Professional-level independence and methodological rigor
- Consider multiple dimensions (economic, ethical, scientific, social, regulatory)
- Work at level expected in industry or graduate school

Independence: Full independence, professional standards expected
Sources: 6+ sources, primarily peer-reviewed or primary research
Time Frame: Semester-long projects or research initiatives
Product: Original research, comprehensive HACCP plans, professional proposals
"""
    }
    
    suggested_verbs = ', '.join(grade_verbs.get(grade_level, grade_verbs['Middle']))
    forbidden_for_level = grade_forbidden.get(grade_level, [])
    forbidden_level_note = ""
    if forbidden_for_level:
        forbidden_level_note = f"\n- For {grade_level} level, DO NOT use these verbs: {', '.join(forbidden_for_level)}"
    
    # Domain-specific framing (from accuracy update)
    domain_framing = _get_domain_framing(domain, apply_food_overlay)
    
    # OPTIMIZED: Concise prompt for faster generation
    prompt = f"""You are an expert educator creating learning objectives for {domain_description}.

PRIMARY DIRECTIVE: ACCURACY FIRST
- Create scientifically/factually accurate objectives for {domain_description}
- Use correct terminology and concepts for this domain
- Do NOT force unrelated concepts into objectives
- Focus on what students genuinely need to learn

LEARNING GOAL: "{user_intent}"

Grade Level: {grade_level}
Domain: {domain_description}
Objectives: EXACTLY {num_objectives}

{domain_framing}

{grade_context[grade_level]}

OUTPUT FORMAT (EXACT):

Lesson Objectives

Grade Level: {grade_level}
Topic: <Extract clear, concise topic from learning goal>

By the end of this lesson, students will be able to:
1. <Objective>
2. <Objective>
... (continue to {num_objectives})

CRITICAL RULES:

Format:
- EXACTLY {num_objectives} objectives — no more, no less
- Numbered list: 1. 2. 3. etc.
- NO extra headings, bullets, commentary, markdown
- NO blank lines between objectives

Objective Requirements:
- ONE complete sentence per objective
- START with measurable action verb (verb-first)
- NEVER "Students will..." (verb must be first word)
- Observable and assessable
- Match {grade_level} complexity level above

Verbs for {grade_level}:
{suggested_verbs}{forbidden_level_note}

FORBIDDEN VERBS (all levels):
learn, understand, know, recognize, comprehend, grasp, be aware, become aware, be familiar, appreciate, explore, study, review, notice, think about, reflect on, consider, teach, introduce, present, cover, discuss

Verb Diversity:
- Max 2 objectives with same verb
- Vary verb choices

Accuracy:
- Use correct {domain_description} terminology
- Age-appropriate for {grade_level}
- NO forced connections to unrelated topics

Generate {num_objectives} objectives now."""
    
    return prompt


def _get_domain_framing(domain: str, apply_food_overlay: bool) -> str:
    """Generate domain-specific framing."""
    
    domain_guidance = {
        'genetics': """
DOMAIN: Genetics & Heredity
Focus: DNA, genes, chromosomes, alleles, Punnett squares, inheritance, genotype vs phenotype, dominant/recessive traits, genetic variation
""",
        'chemistry': """
DOMAIN: Chemistry
Focus: Matter, atoms, molecules, compounds, chemical reactions, acids/bases, pH, periodic table, states of matter, chemical bonds, balancing equations
""",
        'physics': """
DOMAIN: Physics
Focus: Motion, force, energy, Newton's laws, waves, light, sound, electricity, magnetism, thermodynamics, simple machines
""",
        'biology': """
DOMAIN: Biology
Focus: Cell structure/function, ecosystems, energy flow, photosynthesis, respiration, body systems, evolution, adaptation, classification
""",
        'microbiology': """
DOMAIN: Microbiology
Focus: Bacteria, viruses, fungi, microorganisms, microbial growth, disease transmission, immune response, antibiotics, microscopy, culturing
""",
        'food_science': """
DOMAIN: Food Science
Focus: Food safety, sanitation, microbial growth/preservation, storage/handling, cross-contamination, HACCP, food quality, spoilage vs pathogens
""",
        'earth_science': """
DOMAIN: Earth Science
Focus: Rocks, minerals, weather, climate, plate tectonics, water cycle, fossils, geological time, natural resources
""",
        'astronomy': """
DOMAIN: Astronomy
Focus: Solar system, planets, stars, galaxies, universe, Earth's rotation/revolution, moon phases, eclipses, space exploration
""",
        'mathematics': """
DOMAIN: Mathematics
Focus: Number operations, algebra, geometry, statistics, probability, equations, functions, data analysis, proofs
""",
        'general_science': """
DOMAIN: General Science
Focus: Scientific method, inquiry, evidence-based reasoning, patterns in nature, measurement, data collection, systems thinking
"""
    }
    
    base = domain_guidance.get(domain, domain_guidance['general_science'])
    
    if apply_food_overlay:
        return base + """
FOOD CONTEXT: When naturally relevant, connect to food applications
- Food safety implications
- Kitchen/food service contexts
- Industry relevance
- Nutrition or quality aspects

Only include if scientifically accurate and naturally fits. Do NOT force.
"""
    else:
        return base + """
NO food science connections needed for this topic.
"""


# Backward compatibility
def build_generation_prompt(
    category: str,
    topic: str,
    grade_level: str,
    teacher_details: str = None,
    num_objectives: int = 5
) -> str:
    """
    Backward compatible wrapper.
    Converts old format to new routing-based format.
    """
    from domain_routing import route_to_domain
    
    user_intent = teacher_details if teacher_details else topic
    routing_result = route_to_domain(user_intent, grade_level, category)
    
    return build_generation_prompt_final(
        user_intent=user_intent,
        grade_level=grade_level,
        routing_result=routing_result,
        num_objectives=num_objectives
    )


def build_repair_prompt(
    original_prompt: str,
    invalid_output: str,
    validation_errors: list
) -> str:
    """Build repair prompt for fixing validation errors."""
    
    errors_formatted = "\n".join(f"- {error}" for error in validation_errors)
    
    return f"""Previous output had errors. Fix ALL errors. Return ONLY corrected output, NO commentary.

ORIGINAL PROMPT:
{original_prompt}

PREVIOUS OUTPUT (INVALID):
{invalid_output}

ERRORS:
{errors_formatted}

Return ONLY corrected learning objectives in exact format. No explanations."""
