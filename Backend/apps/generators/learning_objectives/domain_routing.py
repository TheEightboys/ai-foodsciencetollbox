"""
Domain Routing Logic - ACCURACY FIRST APPROACH
Determines the appropriate subject domain and whether to apply food science overlay.
"""

import re
from typing import Tuple, Dict


# Domain keyword mappings
DOMAIN_KEYWORDS = {
    'genetics': [
        'punnett', 'allele', 'genotype', 'phenotype', 'heredity', 'mendel', 
        'chromosome', 'dna', 'rna', 'gene', 'dominant', 'recessive', 'trait',
        'inheritance', 'mutation', 'genomic', 'genetic code'
    ],
    'chemistry': [
        'molecule', 'atom', 'compound', 'reaction', 'acid', 'base', 'ph',
        'periodic table', 'element', 'bond', 'ionic', 'covalent', 'solution',
        'mole', 'stoichiometry', 'oxidation', 'reduction', 'catalyst',
        'chemical equation', 'reactant', 'product', 'balance', 'synthesis',
        'decomposition', 'combustion', 'precipitate'
    ],
    'physics': [
        'force', 'motion', 'velocity', 'acceleration', 'momentum', 'energy',
        'kinetic', 'potential', 'gravity', 'friction', 'newton', 'wave',
        'light', 'electricity', 'magnetism', 'thermodynamics'
    ],
    'biology': [
        'cell', 'organism', 'ecosystem', 'photosynthesis', 'respiration',
        'evolution', 'adaptation', 'species', 'taxonomy', 'organ', 'tissue',
        'system', 'anatomy', 'physiology', 'biome', 'population'
    ],
    'microbiology': [
        'bacteria', 'virus', 'microbe', 'microorganism', 'culture', 'petri',
        'microscope', 'pathogen', 'antibiotic', 'infection', 'immune',
        'prokaryote', 'eukaryote', 'fungi', 'colony'
    ],
    'food_science': [
        'food safety', 'contamination', 'foodborne', 'haccp', 'sanitation',
        'spoilage', 'preservation', 'refrigeration', 'cooking', 'kitchen',
        'restaurant', 'meal', 'recipe', 'ingredient', 'culinary', 'nutrition',
        'storage', 'shelf life', 'cross-contamination', 'food handling'
    ],
    'earth_science': [
        'rock', 'mineral', 'weather', 'climate', 'atmosphere', 'ocean',
        'plate tectonics', 'volcano', 'earthquake', 'erosion', 'fossil',
        'geology', 'meteorology', 'geosphere', 'hydrosphere'
    ],
    'astronomy': [
        'star', 'planet', 'galaxy', 'solar system', 'universe', 'telescope',
        'orbit', 'moon', 'sun', 'comet', 'asteroid', 'space', 'cosmology'
    ],
    'mathematics': [
        'equation', 'algebra', 'geometry', 'calculus', 'statistics',
        'probability', 'graph', 'function', 'variable', 'proof', 'theorem'
    ]
}

# Food science overlay indicators
FOOD_OVERLAY_KEYWORDS = [
    'food', 'cooking', 'kitchen', 'meal', 'recipe', 'ingredient', 'restaurant',
    'culinary', 'nutrition', 'diet', 'eating', 'beverage', 'flavor'
]


def detect_domain(user_intent: str, category: str = None) -> Tuple[str, float]:
    """
    Detect the most appropriate subject domain from user intent.
    
    Args:
        user_intent: Natural language description of learning goal
        category: Optional explicit category (may be ignored if clearly wrong)
    
    Returns:
        (domain_name, confidence_score)
        confidence_score: 0.0-1.0, where >0.6 is high confidence
    """
    
    user_intent_lower = user_intent.lower()
    
    # Score each domain
    domain_scores = {}
    
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            if keyword in user_intent_lower:
                score += 1
                matched_keywords.append(keyword)
        
        if score > 0:
            # Normalize by number of keywords in domain
            normalized_score = score / len(keywords)
            domain_scores[domain] = {
                'score': normalized_score,
                'raw_count': score,
                'matched': matched_keywords
            }
    
    # If no strong matches, use 'general_science' as fallback
    if not domain_scores:
        return 'general_science', 0.3
    
    # Get top domain
    top_domain = max(domain_scores.items(), key=lambda x: x[1]['score'])
    domain_name = top_domain[0]
    confidence = min(top_domain[1]['score'] * 10, 1.0)  # Scale up, cap at 1.0
    
    # If explicit category provided and matches detected domain, boost confidence
    if category and category.lower() in domain_name.lower():
        confidence = min(confidence * 1.2, 1.0)
    
    return domain_name, confidence


def should_apply_food_overlay(
    user_intent: str,
    detected_domain: str,
    confidence: float
) -> Tuple[bool, str]:
    """
    Determine if food science overlay should be applied.
    
    Args:
        user_intent: Natural language description of learning goal
        detected_domain: The primary domain detected
        confidence: Confidence in domain detection (0.0-1.0)
    
    Returns:
        (apply_overlay, reason)
    """
    
    user_intent_lower = user_intent.lower()
    
    # Case 1: Primary domain is already food_science
    if detected_domain == 'food_science':
        return True, "Topic is explicitly food science related"
    
    # Case 2: Check for explicit food science keywords
    food_keyword_count = sum(
        1 for keyword in FOOD_OVERLAY_KEYWORDS 
        if keyword in user_intent_lower
    )
    
    if food_keyword_count >= 2:
        return True, f"Multiple food-related terms detected ({food_keyword_count})"
    
    # Case 3: Microbiology with food context
    if detected_domain == 'microbiology' and food_keyword_count >= 1:
        return True, "Microbiology in food context"
    
    # Case 4: Chemistry with food context
    if detected_domain == 'chemistry' and food_keyword_count >= 1:
        return True, "Chemistry in food context"
    
    # Case 5: User explicitly requests food science connection
    food_request_phrases = [
        'food science', 'food safety', 'in food', 'in cooking',
        'in kitchen', 'culinary', 'food-related', 'food application'
    ]
    
    if any(phrase in user_intent_lower for phrase in food_request_phrases):
        return True, "Explicit food science request"
    
    # Default: No overlay
    return False, f"Topic is pure {detected_domain}, no food context detected"


def route_to_domain(
    user_intent: str,
    grade_level: str,
    category: str = None
) -> Dict:
    """
    Main routing function: determines domain and overlay settings.
    
    Args:
        user_intent: What the user wants students to learn/do
        grade_level: Elementary, Middle, High, or College
        category: Optional explicit category (may be overridden)
    
    Returns:
        {
            'domain': str,              # Primary subject domain
            'confidence': float,        # 0.0-1.0
            'apply_food_overlay': bool, # Whether to add food science lens
            'overlay_reason': str,      # Why overlay was/wasn't applied
            'domain_description': str,  # Human-readable domain
            'warning': str or None      # If category conflicts with detected domain
        }
    """
    
    # Detect primary domain
    detected_domain, confidence = detect_domain(user_intent, category)
    
    # Determine if food overlay appropriate
    apply_overlay, overlay_reason = should_apply_food_overlay(
        user_intent, detected_domain, confidence
    )
    
    # Check for category mismatch
    warning = None
    if category and detected_domain != 'general_science':
        # Simple check: does category align with detected domain?
        category_lower = category.lower()
        if (detected_domain not in category_lower and 
            category_lower not in detected_domain and
            category_lower != 'science'):  # 'science' is acceptable for all
            warning = (
                f"Note: Category '{category}' may not match detected topic domain "
                f"'{detected_domain}'. Using detected domain for accuracy."
            )
    
    # Map domain to description
    domain_descriptions = {
        'genetics': 'Genetics & Heredity',
        'chemistry': 'Chemistry',
        'physics': 'Physics',
        'biology': 'Biology',
        'microbiology': 'Microbiology',
        'food_science': 'Food Science',
        'earth_science': 'Earth Science',
        'astronomy': 'Astronomy',
        'mathematics': 'Mathematics',
        'general_science': 'General Science'
    }
    
    return {
        'domain': detected_domain,
        'confidence': confidence,
        'apply_food_overlay': apply_overlay,
        'overlay_reason': overlay_reason,
        'domain_description': domain_descriptions.get(detected_domain, detected_domain),
        'warning': warning
    }
