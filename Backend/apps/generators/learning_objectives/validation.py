"""
Learning Objectives Validation - FINAL CONSOLIDATED VERSION
Combines: Optimized performance + Improved differentiation + Accuracy checks

Fast validation that separates critical errors from warnings.
"""

import re
from typing import List, Tuple, Optional


# Forbidden verbs/phrases (case-insensitive)
FORBIDDEN_VERBS = [
    'learn', 'understand', 'know', 'recognize', 'comprehend', 'grasp',
    'be aware', 'become aware', 'be familiar', 'become familiar',
    'appreciate', 'explore', 'study', 'review', 'gain awareness',
    'notice', 'think about', 'reflect on', 'consider',
    'teach', 'introduce', 'present', 'cover', 'discuss'
]

# IMPROVED: Stronger grade-level forbidden verbs (from differentiation update)
GRADE_FORBIDDEN_VERBS = {
    'Elementary': [
        'analyze', 'evaluate', 'critique', 'synthesize', 'formulate',
        'optimize', 'defend', 'validate', 'assess', 'justify',
        'interpret', 'design', 'develop', 'explain', 'investigate',
        'hypothesize', 'model', 'theorize'
    ],
    'Middle': [
        'critique', 'synthesize', 'formulate', 'optimize', 'defend',
        'validate', 'hypothesize', 'model', 'theorize',
        'analyze', 'evaluate', 'assess', 'justify'
    ],
    'High': [
        'synthesize', 'formulate', 'optimize', 'validate',
        'hypothesize', 'model', 'theorize', 'integrate', 'devise',
        'engineer'
    ],
    'College': [
        'match', 'label', 'sort', 'list', 'name', 'identify', 'show'
    ]
}

# IMPROVED: Expected verbs for positive validation (from differentiation update)
GRADE_EXPECTED_VERBS = {
    'Elementary': [
        'identify', 'describe', 'demonstrate', 'compare', 'classify',
        'list', 'name', 'show', 'label', 'sort', 'match', 'illustrate',
        'apply', 'predict'
    ],
    'Middle': [
        'explain', 'compare', 'contrast', 'categorize', 'organize',
        'distinguish', 'examine', 'investigate', 'determine', 'calculate',
        'relate', 'summarize'
    ],
    'High': [
        'analyze', 'evaluate', 'justify', 'assess', 'propose',
        'design', 'develop', 'interpret', 'predict', 'critique',
        'construct', 'test'
    ],
    'College': [
        'synthesize', 'formulate', 'optimize', 'validate', 'defend',
        'hypothesize', 'model', 'theorize', 'integrate', 'devise',
        'appraise', 'engineer'
    ]
}


def validate_learning_objectives_final(
    output: str,
    grade_level: str,
    user_intent: str = None
) -> Tuple[Optional[dict], List[str], List[str]]:
    """
    FINAL CONSOLIDATED validation with performance optimization.
    
    Separates critical errors (must fix) from warnings (nice to have).
    Only critical errors trigger retry.
    
    Args:
        output: Generated text to validate
        grade_level: Grade level for context
        user_intent: Optional user intent (replaces teacher_details)
    
    Returns:
        (result_dict, critical_errors, warnings)
    """
    
    critical_errors = []
    warnings = []
    
    # CRITICAL: Check required structure
    if 'Grade Level:' not in output:
        critical_errors.append("Missing 'Grade Level:'")
    
    if 'Topic:' not in output:
        critical_errors.append("Missing 'Topic:'")
    
    if 'By the end of this lesson, students will be able to:' not in output:
        critical_errors.append("Missing 'By the end of this lesson, students will be able to:'")
    
    # Extract components
    extracted_grade = _extract_grade_level(output)
    extracted_topic = _extract_topic(output)
    objectives = _extract_objectives(output)
    
    if not objectives:
        critical_errors.append("No objectives found")
        return None, critical_errors, warnings
    
    # CRITICAL: Validate count
    if len(objectives) < 4:
        critical_errors.append(f"Too few objectives: {len(objectives)} (need at least 4)")
    elif len(objectives) > 10:
        critical_errors.append(f"Too many objectives: {len(objectives)} (max 10)")
    
    # Validate each objective (separating critical vs warnings)
    for i, obj in enumerate(objectives, 1):
        obj_critical, obj_warnings = _validate_single_objective_fast(obj, i, grade_level)
        critical_errors.extend(obj_critical)
        warnings.extend(obj_warnings)
    
    # WARNING: Verb diversity (not critical)
    verb_warnings = _check_verb_diversity(objectives)
    warnings.extend(verb_warnings)
    
    # IMPROVED: Grade-level appropriateness check (from differentiation update)
    appropriateness_warnings = _check_grade_appropriateness(objectives, grade_level)
    warnings.extend(appropriateness_warnings)
    
    # WARNING: User intent incorporation (if provided)
    if user_intent and objectives:
        if not _check_intent_incorporated(objectives, user_intent):
            warnings.append("User intent may not be fully reflected (non-critical)")
    
    # Return result if no critical errors
    if len(critical_errors) == 0:
        return {
            'grade_level': extracted_grade or grade_level,
            'topic': extracted_topic or 'Unknown',
            'objectives': objectives,
            'rendered_text': output
        }, [], warnings
    
    return None, critical_errors, warnings


def _extract_grade_level(output: str) -> Optional[str]:
    """Extract grade level."""
    match = re.search(r'Grade Level:\s*(.+)', output, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_topic(output: str) -> Optional[str]:
    """Extract topic."""
    match = re.search(r'Topic:\s*(.+)', output, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_objectives(output: str) -> List[str]:
    """Extract numbered objectives."""
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


def _validate_single_objective_fast(
    objective: str,
    index: int,
    grade_level: str
) -> Tuple[List[str], List[str]]:
    """Validate single objective - returns (critical_errors, warnings)."""
    
    critical_errors = []
    warnings = []
    objective_lower = objective.lower()
    
    # CRITICAL: Complete sentence
    if not objective.endswith('.'):
        critical_errors.append(f"Objective {index}: Missing period")
    
    # CRITICAL: No "Students will"
    if re.match(r'^Students will\b', objective, re.IGNORECASE):
        critical_errors.append(f"Objective {index}: Starts with 'Students will'")
    
    # Extract first word early — needed by multiple checks below
    first_word = objective.split()[0] if objective else ''
    first_word_lower = first_word.lower().rstrip('.,;:')
    
    # CRITICAL: No forbidden verbs as the STARTING verb
    # Only flag if the objective begins with a forbidden verb — occurrences
    # elsewhere in the sentence are acceptable
    for forbidden in FORBIDDEN_VERBS:
        parts = forbidden.split()
        # Single-word forbidden verb: check against first word
        if len(parts) == 1:
            if first_word_lower == forbidden or first_word_lower == forbidden + 's' or first_word_lower == forbidden + 'ing':
                critical_errors.append(f"Objective {index}: Starts with forbidden verb '{forbidden}'")
                break
        else:
            # Multi-word phrase: check the beginning of the objective
            if objective_lower.startswith(forbidden):
                critical_errors.append(f"Objective {index}: Starts with forbidden phrase '{forbidden}'")
                break
    
    # CRITICAL: No grade-inappropriate verbs
    grade_forbidden = GRADE_FORBIDDEN_VERBS.get(grade_level, [])
    if first_word_lower in [v.lower() for v in grade_forbidden]:
        critical_errors.append(f"Objective {index}: Verb '{first_word}' inappropriate for {grade_level}")
    
    # CRITICAL: Starts with verb
    if not first_word or not first_word[0].isupper():
        critical_errors.append(f"Objective {index}: Doesn't start with action verb")
    
    # WARNING: Subject relevance check (relaxed - not critical for accuracy-first)
    # Domain-specific terms will vary, so we don't enforce specific keywords
    
    return critical_errors, warnings


def _check_verb_diversity(objectives: List[str]) -> List[str]:
    """Check verb diversity - returns warnings."""
    warnings = []
    verbs = [obj.split()[0].lower() if obj else '' for obj in objectives]
    
    from collections import Counter
    verb_counts = Counter(verbs)
    
    for verb, count in verb_counts.items():
        if count > 2:
            warnings.append(f"Warning: {count} objectives start with '{verb}' (recommend max 2)")
    
    return warnings


def _check_grade_appropriateness(objectives: List[str], grade_level: str) -> List[str]:
    """Check if objectives use grade-appropriate verbs - returns warnings."""
    warnings = []
    expected_verbs = GRADE_EXPECTED_VERBS.get(grade_level, [])
    
    if not expected_verbs:
        return warnings
    
    objective_verbs = [obj.split()[0].lower() if obj else '' for obj in objectives]
    using_expected = sum(1 for verb in objective_verbs if verb in expected_verbs)
    
    if len(objectives) > 0:
        percentage = (using_expected / len(objectives)) * 100
        if percentage < 60:
            warnings.append(
                f"Only {using_expected}/{len(objectives)} objectives use {grade_level}-appropriate verbs "
                f"({', '.join(expected_verbs[:6])}...)"
            )
    
    return warnings


def _check_intent_incorporated(objectives: List[str], user_intent: str) -> bool:
    """Quick check if user intent reflected in objectives."""
    keywords = _extract_keywords(user_intent)
    if not keywords:
        return True
    
    combined = ' '.join(objectives).lower()
    return any(keyword in combined for keyword in keywords)


def _extract_keywords(text: str) -> List[str]:
    """Extract keywords from text (fast version)."""
    if not text:
        return []
    
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those'
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if len(w) >= 3 and w not in stop_words]
    
    # Remove duplicates, limit to 10 for speed
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
            if len(unique) >= 10:
                break
    
    return unique


# Backward compatibility
def validate_learning_objectives(
    output: str,
    grade_level: str,
    teacher_details: str = None
) -> Tuple[Optional[dict], List[str]]:
    """Backward compatible validation (combines errors + warnings)."""
    
    result, critical_errors, warnings = validate_learning_objectives_final(
        output, grade_level, teacher_details
    )
    
    # Combine for backward compatibility
    all_issues = critical_errors + warnings
    return result, all_issues
