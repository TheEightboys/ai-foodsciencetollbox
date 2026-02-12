"""
Consolidated Validator - COMPREHENSIVE VALIDATION PIPELINE
Brings together all validation improvements:
- Critical vs warning separation
- Grade-appropriateness validation with profiles
- Domain-specific accuracy checks
- Post-processing validation
- Performance optimization
"""

import re
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from ..consolidated.grade_profiles import get_grade_profile, validate_grade_appropriateness


@dataclass
class ValidationResult:
    """Comprehensive validation result."""
    is_valid: bool
    critical_errors: List[str]
    warnings: List[str]
    extracted_data: Optional[Dict[str, Any]]
    quality_score: float
    grade_appropriateness: Dict[str, Any]
    domain_accuracy: Dict[str, Any]


class ConsolidatedValidator:
    """
    CONSOLIDATED validator with comprehensive validation pipeline.
    
    Features:
    1. Critical vs warning separation (only critical trigger retries)
    2. Grade-appropriateness validation using profiles
    3. Domain-specific accuracy checks
    4. Quality scoring
    5. Performance optimization
    """
    
    def __init__(self):
        """Initialize consolidated validator."""
        # Forbidden verbs/phrases (case-insensitive)
        self.forbidden_verbs = [
            'learn', 'understand', 'know', 'recognize', 'comprehend', 'grasp',
            'be aware', 'become aware', 'be familiar', 'become familiar',
            'appreciate', 'explore', 'study', 'review', 'gain awareness',
            'notice', 'think about', 'reflect on', 'consider',
            'teach', 'introduce', 'present', 'cover', 'discuss'
        ]
        
        # Quality weights for scoring
        self.quality_weights = {
            'format_compliance': 0.3,
            'verb_appropriateness': 0.25,
            'objective_quality': 0.2,
            'grade_level_match': 0.15,
            'domain_relevance': 0.1
        }
    
    def validate(
        self,
        output: str,
        grade_level: str,
        user_intent: str = None,
        expected_domain: str = None
    ) -> ValidationResult:
        """
        Comprehensive validation with critical/warning separation.
        
        Args:
            output: Generated text to validate
            grade_level: Grade level for context
            user_intent: Optional user intent for relevance check
            expected_domain: Optional expected domain for accuracy check
        
        Returns:
            ValidationResult with comprehensive validation data
        """
        critical_errors = []
        warnings = []
        
        # Step 1: Critical structure validation
        structure_result = self._validate_structure(output)
        critical_errors.extend(structure_result['critical_errors'])
        warnings.extend(structure_result['warnings'])
        
        if structure_result['critical_errors']:
            # If structure is critically invalid, return early
            return ValidationResult(
                is_valid=False,
                critical_errors=critical_errors,
                warnings=warnings,
                extracted_data=None,
                quality_score=0.0,
                grade_appropriateness={},
                domain_accuracy={}
            )
        
        # Step 2: Extract components
        extracted_data = self._extract_components(output)
        
        # Step 3: Validate objectives count
        count_result = self._validate_objectives_count(extracted_data['objectives'])
        critical_errors.extend(count_result['critical_errors'])
        warnings.extend(count_result['warnings'])
        
        # Step 4: Validate each objective
        objective_results = self._validate_objectives(
            extracted_data['objectives'],
            grade_level
        )
        critical_errors.extend(objective_results['critical_errors'])
        warnings.extend(objective_results['warnings'])
        
        # Step 5: Grade-appropriateness validation
        grade_appropriateness = validate_grade_appropriateness(
            extracted_data['objectives'], grade_level
        )
        warnings.extend(grade_appropriateness['issues'])
        
        # Step 6: Domain accuracy validation
        domain_accuracy = self._validate_domain_accuracy(
            extracted_data['objectives'],
            expected_domain
        )
        warnings.extend(domain_accuracy['warnings'])
        
        # Step 7: User intent relevance
        if user_intent:
            relevance_result = self._validate_intent_relevance(
                extracted_data['objectives'],
                user_intent
            )
            warnings.extend(relevance_result['warnings'])
        
        # Step 8: Calculate quality score
        quality_score = self._calculate_quality_score(
            structure_result,
            objective_results,
            grade_appropriateness,
            domain_accuracy,
            len(critical_errors) == 0
        )
        
        # Step 9: Final validation decision
        is_valid = len(critical_errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            critical_errors=critical_errors,
            warnings=warnings,
            extracted_data=extracted_data,
            quality_score=quality_score,
            grade_appropriateness=grade_appropriateness,
            domain_accuracy=domain_accuracy
        )
    
    def _validate_structure(self, output: str) -> Dict[str, List[str]]:
        """Validate required structure elements."""
        critical_errors = []
        warnings = []
        
        required_headers = [
            'Grade Level:',
            'Topic:',
            'By the end of this lesson, students will be able to:'
        ]
        
        for header in required_headers:
            if header not in output:
                critical_errors.append(f"Missing required header: '{header}'")
        
        # Check for common formatting issues
        if 'Students will' in output:
            warnings.append("Contains 'Students will' - objectives should start with verbs")
        
        if re.search(r'^\s*\d+\.\s*$', output, re.MULTILINE):
            warnings.append("Contains empty numbered items")
        
        return {'critical_errors': critical_errors, 'warnings': warnings}
    
    def _extract_components(self, output: str) -> Dict[str, Any]:
        """Extract components from generated output."""
        # Extract grade level
        grade_match = re.search(r'Grade Level:\s*(.+)', output, re.IGNORECASE)
        extracted_grade = grade_match.group(1).strip() if grade_match else None
        
        # Extract topic
        topic_match = re.search(r'Topic:\s*(.+)', output, re.IGNORECASE)
        extracted_topic = topic_match.group(1).strip() if topic_match else None
        
        # Extract objectives
        objectives = self._extract_objectives(output)
        
        return {
            'grade_level': extracted_grade,
            'topic': extracted_topic,
            'objectives': objectives
        }
    
    def _extract_objectives(self, output: str) -> List[str]:
        """Extract numbered objectives from output."""
        objectives = []
        
        by_end_match = re.search(
            r'By the end of this lesson, students will be able to:\s*\n(.+)',
            output,
            re.DOTALL | re.IGNORECASE
        )
        
        if not by_end_match:
            return objectives
        
        content = by_end_match.group(1).strip()
        pattern = r'^\s*(\d+)[\.\)]\s*(.+?)(?=^\s*\d+[\.\)]|\Z)'
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        
        for num, text in matches:
            cleaned = ' '.join(text.split())
            if cleaned:
                objectives.append(cleaned)
        
        return objectives
    
    def _validate_objectives_count(self, objectives: List[str]) -> Dict[str, List[str]]:
        """Validate number of objectives."""
        critical_errors = []
        warnings = []
        
        count = len(objectives)
        
        if count < 4:
            critical_errors.append(f"Too few objectives: {count} (need at least 4)")
        elif count > 10:
            critical_errors.append(f"Too many objectives: {count} (max 10)")
        elif count < 5:
            warnings.append(f"Only {count} objectives (5 is recommended)")
        
        return {'critical_errors': critical_errors, 'warnings': warnings}
    
    def _validate_objectives(self, objectives: List[str], grade_level: str) -> Dict[str, List[str]]:
        """Validate each objective individually."""
        critical_errors = []
        warnings = []
        
        grade_profile = get_grade_profile(grade_level)
        forbidden_for_grade = [v.lower() for v in grade_profile.forbidden_verbs]
        
        for i, objective in enumerate(objectives, 1):
            obj_critical, obj_warnings = self._validate_single_objective(
                objective, i, forbidden_for_grade
            )
            critical_errors.extend(obj_critical)
            warnings.extend(obj_warnings)
        
        # Check verb diversity
        verb_diversity_issues = self._check_verb_diversity(objectives)
        warnings.extend(verb_diversity_issues)
        
        return {'critical_errors': critical_errors, 'warnings': warnings}
    
    def _validate_single_objective(
        self,
        objective: str,
        index: int,
        forbidden_for_grade: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Validate a single objective."""
        critical_errors = []
        warnings = []
        objective_lower = objective.lower()
        
        # Critical: Complete sentence
        if not objective.endswith('.'):
            critical_errors.append(f"Objective {index}: Missing period")
        
        # Critical: No "Students will"
        if re.match(r'^Students will\b', objective, re.IGNORECASE):
            critical_errors.append(f"Objective {index}: Starts with 'Students will'")
        
        # Critical: Starts with action verb
        words = objective.split()
        if not words or not words[0][0].isupper():
            critical_errors.append(f"Objective {index}: Doesn't start with action verb")
        
        first_word = words[0].lower() if words else ''
        
        # Critical: No forbidden verbs
        for forbidden in self.forbidden_verbs:
            if forbidden in objective_lower:
                critical_errors.append(f"Objective {index}: Contains '{forbidden}'")
                break
        
        # Critical: No grade-inappropriate verbs
        if first_word in forbidden_for_grade:
            critical_errors.append(f"Objective {index}: Verb '{first_word}' inappropriate for grade level")
        
        # Warnings: Quality checks
        if len(objective) < 15:
            warnings.append(f"Objective {index}: Very short (may lack specificity)")
        
        if len(objective) > 100:
            warnings.append(f"Objective {index}: Very long (may be too complex)")
        
        # Warning: Check for measurable language
        measurable_indicators = ['demonstrate', 'calculate', 'create', 'analyze', 'evaluate', 'design', 'compare', 'classify']
        if not any(indicator in objective_lower for indicator in measurable_indicators):
            warnings.append(f"Objective {index}: May not be easily measurable")
        
        return critical_errors, warnings
    
    def _check_verb_diversity(self, objectives: List[str]) -> List[str]:
        """Check for verb diversity."""
        warnings = []
        verbs = []
        
        for obj in objectives:
            if obj and obj.strip():
                first_word = obj.split()[0].lower()
                verbs.append(first_word)
        
        from collections import Counter
        verb_counts = Counter(verbs)
        
        for verb, count in verb_counts.items():
            if count > 2:
                warnings.append(f"Verb diversity: {count} objectives start with '{verb}' (recommend max 2)")
        
        return warnings
    
    def _validate_domain_accuracy(
        self,
        objectives: List[str],
        expected_domain: str
    ) -> Dict[str, Any]:
        """Validate domain-specific accuracy."""
        warnings = []
        domain_relevance_score = 0.0
        
        if not expected_domain or expected_domain == 'general_science':
            return {
                'warnings': warnings,
                'relevance_score': 0.5,  # Neutral for general science
                'matched_terms': []
            }
        
        # Domain-specific keywords
        domain_keywords = {
            'genetics': ['gene', 'dna', 'chromosome', 'allele', 'trait', 'inheritance', 'genotype', 'phenotype'],
            'chemistry': ['atom', 'molecule', 'compound', 'reaction', 'chemical', 'bond', 'element', 'solution'],
            'physics': ['force', 'motion', 'energy', 'velocity', 'acceleration', 'wave', 'electricity', 'magnetism'],
            'biology': ['cell', 'organism', 'ecosystem', 'evolution', 'species', 'organ', 'tissue', 'system'],
            'microbiology': ['bacteria', 'virus', 'microbe', 'microorganism', 'pathogen', 'infection', 'immune'],
            'food_science': ['food', 'safety', 'contamination', 'preservation', 'storage', 'handling', 'spoilage'],
            'earth_science': ['rock', 'mineral', 'weather', 'climate', 'erosion', 'fossil', 'geology'],
            'astronomy': ['star', 'planet', 'galaxy', 'solar', 'orbit', 'space', 'telescope', 'universe'],
            'mathematics': ['equation', 'calculate', 'function', 'variable', 'graph', 'statistic', 'probability']
        }
        
        keywords = domain_keywords.get(expected_domain, [])
        matched_terms = []
        
        for objective in objectives:
            obj_lower = objective.lower()
            for keyword in keywords:
                if keyword in obj_lower:
                    matched_terms.append(keyword)
        
        # Calculate relevance score
        if keywords:
            domain_relevance_score = len(set(matched_terms)) / len(keywords)
        
        # Check for domain mismatches
        if domain_relevance_score < 0.2:
            warnings.append(f"Low domain relevance for {expected_domain}: few domain-specific terms found")
        
        return {
            'warnings': warnings,
            'relevance_score': domain_relevance_score,
            'matched_terms': list(set(matched_terms))
        }
    
    def _validate_intent_relevance(
        self,
        objectives: List[str],
        user_intent: str
    ) -> Dict[str, List[str]]:
        """Validate if objectives reflect user intent."""
        warnings = []
        
        # Extract keywords from user intent
        intent_keywords = self._extract_keywords(user_intent)
        
        if not intent_keywords:
            return {'warnings': warnings}
        
        # Check if objectives contain intent keywords
        combined_objectives = ' '.join(objectives).lower()
        matched_keywords = [kw for kw in intent_keywords if kw in combined_objectives]
        
        relevance_score = len(matched_keywords) / len(intent_keywords) if intent_keywords else 0
        
        if relevance_score < 0.3:
            warnings.append("Objectives may not fully reflect user intent")
        
        return {'warnings': warnings}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'want', 'need', 'learn', 'understand'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) >= 3 and w not in stop_words]
        
        # Remove duplicates, limit to 10
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
                if len(unique) >= 10:
                    break
        
        return unique
    
    def _calculate_quality_score(
        self,
        structure_result: Dict,
        objective_results: Dict,
        grade_appropriateness: Dict,
        domain_accuracy: Dict,
        is_valid: bool
    ) -> float:
        """Calculate overall quality score."""
        if not is_valid:
            return 0.0
        
        scores = {}
        
        # Format compliance (0-1)
        scores['format_compliance'] = 1.0 if len(structure_result['critical_errors']) == 0 else 0.0
        
        # Verb appropriateness (0-1)
        scores['verb_appropriateness'] = grade_appropriateness.get('percentage', 0) / 100.0
        
        # Objective quality (0-1, inverse of warning count)
        warning_count = len(objective_results['warnings'])
        scores['objective_quality'] = max(0.0, 1.0 - (warning_count * 0.1))
        
        # Grade level match (0-1)
        scores['grade_level_match'] = 1.0  # Assuming extracted grade matches input
        
        # Domain relevance (0-1)
        scores['domain_relevance'] = domain_accuracy.get('relevance_score', 0.5)
        
        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in self.quality_weights.items():
            if metric in scores:
                total_score += scores[metric] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0


# Backward compatibility wrapper
def validate_consolidated_learning_objectives(
    output: str,
    grade_level: str,
    user_intent: str = None,
    expected_domain: str = None
) -> Tuple[Optional[Dict], List[str], List[str]]:
    """
    Backward compatibility wrapper for consolidated validator.
    
    Returns:
        (result_dict, critical_errors, warnings)
    """
    validator = ConsolidatedValidator()
    result = validator.validate(output, grade_level, user_intent, expected_domain)
    
    if result.is_valid:
        return result.extracted_data, [], result.warnings
    else:
        return None, result.critical_errors, result.warnings
