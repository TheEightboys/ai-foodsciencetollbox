"""
Grade Profiles - COMPREHENSIVE GRADE-LEVEL COMPLEXITY DESCRIPTORS
Defines detailed complexity profiles for each grade level with:
- Cognitive complexity levels
- Expected independence levels
- Appropriate verb taxonomies
- Context and source expectations
- Time frame and product expectations
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class GradeProfile:
    """Comprehensive grade-level profile."""
    name: str
    cognitive_level: str
    independence_level: str
    expected_verbs: List[str]
    forbidden_verbs: List[str]
    complexity_guidance: str
    context_expectations: str
    source_expectations: str
    time_frame: str
    expected_products: str
    teacher_support: str


# COMPREHENSIVE GRADE PROFILES
GRADE_PROFILES: Dict[str, GradeProfile] = {
    'Elementary': GradeProfile(
        name='Elementary (K-5)',
        cognitive_level='Basic, concrete understanding with direct instruction',
        independence_level='High teacher support and scaffolding required',
        expected_verbs=[
            'Identify', 'Describe', 'Demonstrate', 'Compare', 'Classify',
            'List', 'Name', 'Show', 'Label', 'Sort', 'Match', 'Illustrate',
            'Apply', 'Predict', 'Recognize', 'Find', 'Locate', 'Draw'
        ],
        forbidden_verbs=[
            'Analyze', 'Evaluate', 'Critique', 'Synthesize', 'Formulate',
            'Optimize', 'Defend', 'Validate', 'Assess', 'Justify',
            'Interpret', 'Design', 'Develop', 'Explain', 'Investigate',
            'Hypothesize', 'Model', 'Theorize', 'Critique', 'Appraise'
        ],
        complexity_guidance="""
COMPLEXITY LEVEL: Basic, concrete understanding with direct instruction

Expectations:
- Students identify and describe observable phenomena
- Focus on what students can see, touch, or directly experience
- Simple cause-and-effect relationships (1-2 variables)
- Guided practice with clear teacher modeling
- Familiar, everyday contexts (home, school, playground)
- Concrete examples, no abstract concepts

Cognitive Load:
- Single-step problems
- Direct instruction preferred
- Visual and hands-on learning
- Repetition and practice important
- Immediate feedback expected
""",
        context_expectations="""
CONTEXT EXPECTATIONS:
- Familiar, everyday environments
- School, home, playground, neighborhood
- Concrete objects and experiences
- Simple, relatable scenarios
- Age-appropriate examples

Avoid:
- Abstract concepts
- Complex social systems
- Theoretical frameworks
- Multi-step abstract reasoning
""",
        source_expectations="""
SOURCE EXPECTATIONS:
- 1-2 sources maximum
- Teacher-provided materials
- Textbook excerpts
- Direct observation
- Hands-on demonstrations
- Visual aids and manipulatives

No independent research expected
""",
        time_frame='Single class period activities (30-60 minutes)',
        expected_products="""
EXPECTED PRODUCTS:
- Simple demonstrations
- Basic worksheets
- Concrete examples
- Drawings or illustrations
- Oral responses
- Matching activities
- Show-and-tell presentations
""",
        teacher_support="""
TEACHER SUPPORT LEVEL: HIGH
- Direct instruction required
- Step-by-step guidance
- Frequent check-ins
- Modeling of procedures
- Immediate feedback
- Scaffolding for all tasks
"""
    ),
    
    'Middle': GradeProfile(
        name='Middle School (6-8)',
        cognitive_level='Conceptual understanding with structured frameworks',
        independence_level='Moderate support with structured frameworks',
        expected_verbs=[
            'Explain', 'Compare', 'Contrast', 'Categorize', 'Organize',
            'Distinguish', 'Examine', 'Investigate', 'Determine', 'Calculate',
            'Relate', 'Summarize', 'Analyze', 'Interpret', 'Apply'
        ],
        forbidden_verbs=[
            'Critique', 'Synthesize', 'Formulate', 'Optimize', 'Defend',
            'Validate', 'Hypothesize', 'Model', 'Theorize',
            'Engineer', 'Devise', 'Integrate', 'Appraise'
        ],
        complexity_guidance="""
COMPLEXITY LEVEL: Conceptual understanding with structured frameworks

Expectations:
- Students explain processes and relationships between concepts
- Focus on WHY things happen and HOW they work
- Compare 2-4 approaches using teacher-provided criteria
- Work with structured frameworks and guiding questions
- Handle multi-factor situations (3-4 variables) with some independence
- Developing abstract thinking, using models and diagrams

Cognitive Load:
- Multi-step problems with guidance
- Beginning abstract reasoning
- Pattern recognition
- Basic analysis of relationships
- Structured inquiry approaches
""",
        context_expectations="""
CONTEXT EXPECTATIONS:
- School and community contexts
- Scientific phenomena with explanations
- Historical events with cause-effect
- Mathematical patterns and relationships
- Environmental systems
- Simple technological applications

Balance of concrete and abstract:
- Start with concrete examples
- Bridge to abstract concepts
- Use models and representations
""",
        source_expectations="""
SOURCE EXPECTATIONS:
- 2-4 provided sources with guiding questions
- Textbook chapters with comprehension questions
- Teacher-curated articles
- Structured web research with guidance
- Data sets with analysis frameworks
- Primary sources with scaffolding

Beginning independent source evaluation:
- Compare multiple perspectives
- Identify bias with guidance
- Basic source reliability assessment
""",
        time_frame='Multiple class periods or short projects (1-2 weeks)',
        expected_products="""
EXPECTED PRODUCTS:
- Organized reports
- Comparison charts
- Structured investigations
- Data analysis with graphs
- Lab reports with templates
- Research summaries
- Presentations with outlines
- Models and diagrams
""",
        teacher_support="""
TEACHER SUPPORT LEVEL: MODERATE
- Structured frameworks provided
- Guiding questions and rubrics
- Checkpoints and milestones
- Peer collaboration opportunities
- Teacher as facilitator
- Scaffolding gradually reduced
"""
    ),
    
    'High': GradeProfile(
        name='High School (9-12)',
        cognitive_level='Analysis and application with significant independence',
        independence_level='Minimal scaffolding, student-driven inquiry',
        expected_verbs=[
            'Analyze', 'Evaluate', 'Justify', 'Assess', 'Propose',
            'Design', 'Develop', 'Interpret', 'Predict', 'Critique',
            'Construct', 'Test', 'Compare', 'Contrast', 'Explain'
        ],
        forbidden_verbs=[
            'Synthesize', 'Formulate', 'Optimize', 'Validate',
            'Hypothesize', 'Model', 'Theorize', 'Integrate', 'Devise',
            'Engineer', 'Appraise', 'Defend'
        ],
        complexity_guidance="""
COMPLEXITY LEVEL: Analysis and application with significant independence

Expectations:
- Students independently analyze complex, multi-variable scenarios
- Evaluate situations and justify decisions using evidence
- Design solutions to authentic, real-world problems
- Work with minimal scaffolding or teacher support
- Handle conflicting information and make trade-off decisions
- Apply knowledge to novel situations not directly taught

Cognitive Load:
- Complex, multi-step problem solving
- Independent analysis and evaluation
- Application to novel contexts
- Evidence-based reasoning
- Critical thinking and judgment
""",
        context_expectations="""
CONTEXT EXPECTATIONS:
- Real-world problems and scenarios
- Current events and issues
- Professional and workplace contexts
- Complex systems and interactions
- Global and cultural perspectives
- Ethical and social implications

Authentic contexts:
- Community issues
- Environmental challenges
- Technological applications
- Historical parallels to current events
- Career-related scenarios
""",
        source_expectations="""
SOURCE EXPECTATIONS:
- 4-6 sources, students find some independently
- Mix of primary and secondary sources
- Academic articles and professional publications
- Government reports and data
- Professional websites and databases
- Interviews with experts (when possible)

Advanced source skills:
- Independent source location
- Credibility evaluation
- Synthesis of multiple perspectives
- Identification of bias and limitations
- Proper citation practices
""",
        time_frame='Extended projects and investigations (2-4 weeks)',
        expected_products="""
EXPECTED PRODUCTS:
- Research papers with citations
- Original designs and prototypes
- Evidence-based arguments
- Case study analyses
- Policy proposals
- Lab investigations with original questions
- Multimedia presentations
- Portfolio-quality work
""",
        teacher_support="""
TEACHER SUPPORT LEVEL: MINIMAL
- Consultation and feedback
- Resource recommendations
- Assessment rubrics provided
- Progress monitoring
- Teacher as consultant/expert
- Student-led conferences
"""
    ),
    
    'College': GradeProfile(
        name='College/University',
        cognitive_level='Synthesis and professional-level critical thinking',
        independence_level='Full independence, professional standards expected',
        expected_verbs=[
            'Synthesize', 'Formulate', 'Optimize', 'Validate', 'Defend',
            'Hypothesize', 'Model', 'Theorize', 'Integrate', 'Devise',
            'Appraise', 'Engineer', 'Design', 'Develop', 'Analyze'
        ],
        forbidden_verbs=[
            'Match', 'Label', 'Sort', 'List', 'Name', 'Identify', 'Show',
            'Recognize', 'Find', 'Locate'  # Basic skills not college-level
        ],
        complexity_guidance="""
COMPLEXITY LEVEL: Synthesis and professional-level critical thinking

Expectations:
- Students synthesize information from multiple primary sources
- Create new frameworks, comprehensive plans, or theoretical models
- Critique existing practices using current research and theory
- Professional-level independence and methodological rigor
- Consider multiple dimensions (economic, ethical, scientific, social, regulatory)
- Work at level expected in industry or graduate school

Cognitive Load:
- Original research and analysis
- Creation of new knowledge or frameworks
- Professional-level problem solving
- Interdisciplinary thinking
- Advanced theoretical reasoning
""",
        context_expectations="""
CONTEXT EXPECTATIONS:
- Professional and industry contexts
- Current research and theoretical debates
- Complex, multi-stakeholder environments
- Global and systemic challenges
- Emerging technologies and innovations
- Regulatory and policy frameworks

Professional contexts:
- Industry standards and practices
- Research laboratory environments
- Policy and governance scenarios
- Entrepreneurial ventures
- Consulting and advisory contexts
""",
        source_expectations="""
SOURCE EXPECTATIONS:
- 6+ sources, primarily peer-reviewed or primary research
- Current academic journals and conference proceedings
- Professional standards and industry reports
- Government and policy documents
- Patents and technical documentation
- Expert interviews and professional networks

Graduate-level source skills:
- Comprehensive literature reviews
- Critical analysis of methodology
- Identification of research gaps
- Synthesis across disciplines
- Contribution to scholarly conversation
""",
        time_frame='Semester-long projects or research initiatives',
        expected_products="""
EXPECTED PRODUCTS:
- Original research papers
- Comprehensive plans (HACCP, business, etc.)
- Professional proposals and reports
- Theoretical models or frameworks
- Patent applications
- Policy analyses and recommendations
- Conference presentations
- Thesis-quality work
""",
        teacher_support="""
TEACHER SUPPORT LEVEL: PROFESSIONAL MENTORSHIP
- Advisor/mentor relationship
- Professional networking opportunities
- Research guidance and methodology support
- Career and professional development
- Peer review and critique
- Independent study supervision
"""
    )
}


def get_grade_profile(grade_level: str) -> GradeProfile:
    """
    Get grade profile for given grade level.
    
    Args:
        grade_level: Elementary, Middle, High, or College
    
    Returns:
        GradeProfile object with comprehensive complexity descriptors
    """
    return GRADE_PROFILES.get(grade_level, GRADE_PROFILES['High'])  # Default to High


def get_grade_verbs(grade_level: str) -> Dict[str, List[str]]:
    """
    Get expected and forbidden verbs for grade level.
    
    Returns:
        {'expected': [...], 'forbidden': [...]}
    """
    profile = get_grade_profile(grade_level)
    return {
        'expected': profile.expected_verbs,
        'forbidden': profile.forbidden_verbs
    }


def validate_grade_appropriateness(objectives: List[str], grade_level: str) -> Dict:
    """
    Validate if objectives use grade-appropriate verbs.
    
    Returns:
        {
            'appropriate_count': int,
            'total_count': int,
            'percentage': float,
            'issues': List[str]
        }
    """
    profile = get_grade_profile(grade_level)
    expected_verbs = [v.lower() for v in profile.expected_verbs]
    forbidden_verbs = [v.lower() for v in profile.forbidden_verbs]
    
    appropriate_count = 0
    issues = []
    
    for i, objective in enumerate(objectives, 1):
        if not objective or not objective.strip():
            continue
            
        first_word = objective.split()[0].lower()
        
        # Check forbidden verbs
        if first_word in forbidden_verbs:
            issues.append(f"Objective {i}: Verb '{first_word}' too basic for {grade_level} level")
        # Check expected verbs
        elif first_word in expected_verbs:
            appropriate_count += 1
    
    total_count = len([o for o in objectives if o and o.strip()])
    percentage = (appropriate_count / total_count * 100) if total_count > 0 else 0
    
    return {
        'appropriate_count': appropriate_count,
        'total_count': total_count,
        'percentage': percentage,
        'issues': issues
    }
