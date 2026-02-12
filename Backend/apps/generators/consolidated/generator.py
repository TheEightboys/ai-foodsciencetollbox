"""
Consolidated Generator - CANONICAL IMPLEMENTATION
Brings together all improvements:
- Domain routing for accuracy-first approach
- Grade profiles with complexity descriptors
- Single-prompt design with user_intent
- Strict validation with critical/warning separation
- Performance optimization (2 attempts max)
- Comprehensive observability
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Tuple, Any
import time
import logging
from ..shared.llm_client import LLMClient
from ..consolidated.grade_profiles import get_grade_profile, validate_grade_appropriateness
from ..learning_objectives.domain_routing import route_to_domain
from ..learning_objectives.validation import validate_learning_objectives_final

logger = logging.getLogger(__name__)


@dataclass
class ConsolidatedInput:
    """
    CONSOLIDATED INPUT MODEL - Single prompt design.
    
    Primary field: user_intent (what teacher wants students to learn)
    Grade level: drives complexity via grade profiles
    """
    user_intent: str  # Required: Natural language learning goal
    grade_level: str  # Required: Elementary, Middle, High, College
    num_objectives: int = 5  # Optional: 4-10, default 5
    
    def __post_init__(self):
        """Validate inputs."""
        valid_grades = ['Elementary', 'Middle', 'High', 'College']
        if self.grade_level not in valid_grades:
            raise ValueError(f"grade_level must be one of {valid_grades}, got '{self.grade_level}'")
        
        if not (4 <= self.num_objectives <= 10):
            raise ValueError(f"num_objectives must be 4-10, got {self.num_objectives}")
        
        if not self.user_intent or not self.user_intent.strip():
            raise ValueError("user_intent is required and cannot be empty")
        
        if len(self.user_intent.strip()) < 10:
            raise ValueError("user_intent must be at least 10 characters long")


class ConsolidatedGenerator:
    """
    CONSOLIDATED generator with all optimizations and improvements.
    
    Key Features:
    1. Single-prompt design with user_intent
    2. Domain routing for accuracy-first approach
    3. Grade profiles with detailed complexity descriptors
    4. Strict validation with critical/warning separation
    5. Performance optimization (2 attempts max)
    6. Comprehensive observability and metrics
    7. Post-processing pipeline
    """
    
    def __init__(self, llm_client: LLMClient, max_attempts: int = 2):
        """
        Initialize consolidated generator.
        
        Args:
            llm_client: LLM client for generation
            max_attempts: Max attempts (default 2, optimized for performance)
        """
        self.llm_client = llm_client
        self.max_attempts = max_attempts
        self.metrics = {
            'generations_completed': 0,
            'total_attempts': 0,
            'average_generation_time': 0.0,
            'success_rate': 0.0,
            'domain_distribution': {},
            'grade_distribution': {}
        }
    
    def generate(self, inputs: ConsolidatedInput) -> Dict:
        """
        Generate learning objectives with consolidated approach.
        
        Args:
            inputs: ConsolidatedInput with user_intent and grade_level
        
        Returns:
            Comprehensive result dict with all metadata and observability data
        """
        start_time = time.time()
        
        # Update metrics
        self.metrics['generations_completed'] += 1
        self.metrics['grade_distribution'][inputs.grade_level] = \
            self.metrics['grade_distribution'].get(inputs.grade_level, 0) + 1
        
        try:
            # Step 1: Domain routing for accuracy-first approach
            routing_result = route_to_domain(
                user_intent=inputs.user_intent,
                grade_level=inputs.grade_level,
                category=None  # No category in new design
            )
            
            # Update domain metrics
            domain = routing_result['domain']
            self.metrics['domain_distribution'][domain] = \
                self.metrics['domain_distribution'].get(domain, 0) + 1
            
            # Step 2: Build consolidated prompt with grade profiles
            prompt = self._build_consolidated_prompt(
                user_intent=inputs.user_intent,
                grade_level=inputs.grade_level,
                routing_result=routing_result,
                num_objectives=inputs.num_objectives
            )
            
            # Step 3: Generation loop with validation
            result = self._generate_with_validation(
                prompt=prompt,
                inputs=inputs,
                routing_result=routing_result
            )
            
            # Step 4: Post-processing pipeline
            processed_result = self._post_process_result(result, inputs, routing_result)
            
            # Step 5: Update performance metrics
            generation_time = time.time() - start_time
            self._update_performance_metrics(generation_time, processed_result['success'])
            
            # Add observability data
            processed_result['observability'] = {
                'generation_time': generation_time,
                'attempts_used': processed_result.get('attempts', 0),
                'routing_info': routing_result,
                'grade_profile': asdict(get_grade_profile(inputs.grade_level)),
                'validation_summary': {
                    'critical_errors': len(processed_result.get('critical_errors', [])),
                    'warnings': len(processed_result.get('warnings', [])),
                    'grade_appropriateness': processed_result.get('grade_appropriateness', {})
                }
            }
            
            return processed_result
            
        except Exception as e:
            generation_time = time.time() - start_time
            self._update_performance_metrics(generation_time, False)
            
            logger.error(f"Consolidated generation failed: {e}", exc_info=True)
            
            return {
                'success': False,
                'error': str(e),
                'observability': {
                    'generation_time': generation_time,
                    'attempts_used': self.max_attempts,
                    'routing_info': routing_result if 'routing_result' in locals() else None,
                    'error_type': type(e).__name__
                }
            }
    
    def _build_consolidated_prompt(
        self,
        user_intent: str,
        grade_level: str,
        routing_result: Dict,
        num_objectives: int
    ) -> str:
        """
        Build consolidated prompt with grade profiles and domain routing.
        """
        # Get grade profile
        grade_profile = get_grade_profile(grade_level)
        grade_verbs = get_grade_profile(grade_level)
        
        # Domain-specific framing
        domain = routing_result['domain']
        apply_food_overlay = routing_result['apply_food_overlay']
        domain_description = routing_result['domain_description']
        
        # Build domain context
        domain_context = self._get_domain_context(domain, apply_food_overlay)
        
        # Build verb guidance
        suggested_verbs = ', '.join(grade_verbs.expected_verbs[:15])  # Limit for prompt length
        forbidden_verbs = ', '.join(grade_verbs.forbidden_verbs[:10])  # Limit for prompt length
        
        # Build the consolidated prompt
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

{domain_context}

GRADE PROFILE: {grade_profile.name}
{grade_profile.complexity_guidance}

EXPECTED PRODUCTS:
{grade_profile.expected_products}

TEACHER SUPPORT LEVEL:
{grade_profile.teacher_support}

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
{suggested_verbs}

AVOID these verbs (too basic for {grade_level}):
{forbidden_verbs}

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
    
    def _get_domain_context(self, domain: str, apply_food_overlay: bool) -> str:
        """Get domain-specific context."""
        domain_guidance = {
            'genetics': "DOMAIN: Genetics & Heredity\nFocus: DNA, genes, chromosomes, alleles, Punnett squares, inheritance, genotype vs phenotype, dominant/recessive traits, genetic variation",
            'chemistry': "DOMAIN: Chemistry\nFocus: Matter, atoms, molecules, compounds, chemical reactions, acids/bases, pH, periodic table, states of matter, chemical bonds, balancing equations",
            'physics': "DOMAIN: Physics\nFocus: Motion, force, energy, Newton's laws, waves, light, sound, electricity, magnetism, thermodynamics, simple machines",
            'biology': "DOMAIN: Biology\nFocus: Cell structure/function, ecosystems, energy flow, photosynthesis, respiration, body systems, evolution, adaptation, classification",
            'microbiology': "DOMAIN: Microbiology\nFocus: Bacteria, viruses, fungi, microorganisms, microbial growth, disease transmission, immune response, antibiotics, microscopy, culturing",
            'food_science': "DOMAIN: Food Science\nFocus: Food safety, sanitation, microbial growth/preservation, storage/handling, cross-contamination, HACCP, food quality, spoilage vs pathogens",
            'earth_science': "DOMAIN: Earth Science\nFocus: Rocks, minerals, weather, climate, plate tectonics, water cycle, fossils, geological time, natural resources",
            'astronomy': "DOMAIN: Astronomy\nFocus: Solar system, planets, stars, galaxies, universe, Earth's rotation/revolution, moon phases, eclipses, space exploration",
            'mathematics': "DOMAIN: Mathematics\nFocus: Number operations, algebra, geometry, statistics, probability, equations, functions, data analysis, proofs",
            'general_science': "DOMAIN: General Science\nFocus: Scientific method, inquiry, evidence-based reasoning, patterns in nature, measurement, data collection, systems thinking"
        }
        
        base = domain_guidance.get(domain, domain_guidance['general_science'])
        
        if apply_food_overlay:
            return base + "\n\nFOOD CONTEXT: When naturally relevant, connect to food applications\n- Food safety implications\n- Kitchen/food service contexts\n- Industry relevance\n- Nutrition or quality aspects\n\nOnly include if scientifically accurate and naturally fits. Do NOT force."
        else:
            return base + "\n\nNO food science connections needed for this topic."
    
    def _generate_with_validation(
        self,
        prompt: str,
        inputs: ConsolidatedInput,
        routing_result: Dict
    ) -> Dict:
        """
        Generate with validation loop.
        """
        current_prompt = prompt
        last_output = None
        last_critical_errors = []
        all_warnings = []
        
        for attempt in range(1, self.max_attempts + 1):
            self.metrics['total_attempts'] += 1
            
            try:
                # Generate — pass a dedicated system message to help free models
                # follow the exact output structure
                system_msg = (
                    "You are an expert educator. Follow the OUTPUT FORMAT exactly. "
                    "Return ONLY the formatted output, no commentary. "
                    "The line 'By the end of this lesson, students will be able to:' "
                    "MUST appear on its own line followed by a newline, then numbered objectives."
                )
                output = self.llm_client.generate_text(current_prompt, system_message=system_msg)
                last_output = output
                
                # Validate with critical/warning separation
                result, critical_errors, warnings = validate_learning_objectives_final(
                    output=output,
                    grade_level=inputs.grade_level,
                    user_intent=inputs.user_intent
                )
                
                all_warnings.extend(warnings)
                
                if result:
                    # Additional grade-appropriateness validation
                    grade_validation = validate_grade_appropriateness(
                        result['objectives'], inputs.grade_level
                    )
                    
                    return {
                        'success': True,
                        'grade_level': result['grade_level'],
                        'topic': result['topic'],
                        'objectives': result['objectives'],
                        'rendered_text': result['rendered_text'],
                        'attempts': attempt,
                        'critical_errors': [],
                        'warnings': all_warnings,
                        'grade_appropriateness': grade_validation,
                        'routing': routing_result
                    }
                
                # If we have critical errors, try to repair
                last_critical_errors = critical_errors
                
                if attempt < self.max_attempts:
                    current_prompt = self._build_repair_prompt(
                        original_prompt=prompt,
                        invalid_output=output,
                        validation_errors=critical_errors
                    )
                    
            except Exception as e:
                logger.error(f"Generation attempt {attempt} failed: {e}")
                if attempt == self.max_attempts:
                    raise ValueError(f"LLM generation failed after {attempt} attempts: {str(e)}")
                continue
        
        # Failed after all attempts
        return {
            'success': False,
            'critical_errors': last_critical_errors,
            'warnings': all_warnings,
            'attempts': self.max_attempts,
            'last_output': last_output
        }
    
    def _build_repair_prompt(
        self,
        original_prompt: str,
        invalid_output: str,
        validation_errors: List[str]
    ) -> str:
        """Build repair prompt for fixing validation errors."""
        
        errors_formatted = "\n".join(f"- {error}" for error in validation_errors)
        
        return f"""Previous output had CRITICAL ERRORS that must be fixed. Fix ALL errors. Return ONLY corrected output, NO commentary.

ORIGINAL PROMPT:
{original_prompt}

PREVIOUS OUTPUT (INVALID):
{invalid_output}

CRITICAL ERRORS:
{errors_formatted}

Return ONLY corrected learning objectives in exact format. No explanations."""
    
    def _post_process_result(self, result: Dict, inputs: ConsolidatedInput, routing_result: Dict) -> Dict:
        """
        Post-processing pipeline for generated results.
        """
        if not result.get('success', False):
            return result
        
        # Clean objectives
        objectives = result.get('objectives', [])
        cleaned_objectives = []
        
        for obj in objectives:
            # Remove any remaining artifacts
            cleaned = obj.strip()
            # Ensure proper ending
            if not cleaned.endswith('.'):
                cleaned += '.'
            cleaned_objectives.append(cleaned)
        
        result['objectives'] = cleaned_objectives
        
        # Update rendered text with cleaned objectives
        if 'rendered_text' in result:
            rendered_lines = result['rendered_text'].split('\n')
            new_lines = []
            obj_index = 0
            
            for line in rendered_lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    if obj_index < len(cleaned_objectives):
                        new_lines.append(f"{obj_index + 1}. {cleaned_objectives[obj_index]}")
                        obj_index += 1
                else:
                    new_lines.append(line)
            
            result['rendered_text'] = '\n'.join(new_lines)
        
        # Add success metrics
        result['quality_metrics'] = {
            'objectives_generated': len(cleaned_objectives),
            'target_objectives': inputs.num_objectives,
            'grade_level_match': result.get('grade_level') == inputs.grade_level,
            'domain_confidence': routing_result.get('confidence', 0.0),
            'has_food_overlay': routing_result.get('apply_food_overlay', False)
        }
        
        return result
    
    def _update_performance_metrics(self, generation_time: float, success: bool):
        """Update performance metrics."""
        # Update average generation time
        total_time = self.metrics['average_generation_time'] * (self.metrics['generations_completed'] - 1)
        self.metrics['average_generation_time'] = (total_time + generation_time) / self.metrics['generations_completed']
        
        # Update success rate
        if success:
            current_successes = self.metrics['success_rate'] * (self.metrics['generations_completed'] - 1)
            self.metrics['success_rate'] = (current_successes + 1) / self.metrics['generations_completed']
        else:
            current_successes = self.metrics['success_rate'] * (self.metrics['generations_completed'] - 1)
            self.metrics['success_rate'] = current_successes / self.metrics['generations_completed']
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            'generations_completed': 0,
            'total_attempts': 0,
            'average_generation_time': 0.0,
            'success_rate': 0.0,
            'domain_distribution': {},
            'grade_distribution': {}
        }


# Convenience function for easy usage
def generate_consolidated_learning_objectives(
    llm_client: LLMClient,
    user_intent: str,
    grade_level: str,
    num_objectives: int = 5,
    max_attempts: int = 2
) -> Dict:
    """
    Convenience function to generate learning objectives using consolidated approach.
    
    Args:
        llm_client: LLM client
        user_intent: Natural language description of learning goal
        grade_level: Elementary, Middle, High, or College
        num_objectives: Target number (4-10, default 5)
        max_attempts: Max attempts (default 2)
    
    Returns:
        Comprehensive result dict with observability data
    """
    generator = ConsolidatedGenerator(llm_client, max_attempts)
    inputs = ConsolidatedInput(
        user_intent=user_intent,
        grade_level=grade_level,
        num_objectives=num_objectives
    )
    return generator.generate(inputs)
