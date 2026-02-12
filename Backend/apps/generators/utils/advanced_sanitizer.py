"""
Enterprise-grade advanced input sanitizer with ML-based detection.
Protects against unicode evasion, encoding attacks, and indirect injection.
"""

import re
import base64
import binascii
import unicodedata
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from django.conf import settings
from django.core.cache import cache
from transformers import pipeline
import logging

from ..exceptions import PromptInjectionError

logger = logging.getLogger(__name__)


class AdvancedInputSanitizer:
    """
    Enterprise-grade input sanitizer with multiple layers of protection.
    """
    
    # Advanced patterns for indirect injection
    ADVANCED_PATTERNS = [
        # Context switching attacks
        r'(?i)(you are now|act as|pretend to be|roleplay as)',
        r'(?i)(from now on|starting now|beginning now)',
        r'(?i)(your name is|you are called|call yourself)',
        r'(?i)(new instruction|updated task|modified request)',
        
        # Encoding-based attacks
        r'(base64|b64|hex|encode|decode|unicode|utf)',
        r'\\u[0-9a-fA-F]{4}',  # Unicode escapes
        r'&#\d+;',  # HTML entities
        r'%[0-9A-Fa-f]{2}',  # URL encoding
        
        # Indirect instruction through examples
        r'(?i)(for example|for instance|such as).*(ignore|forget|bypass)',
        r'(?i)(here\'s how|this is how|the way to).*(hack|exploit|bypass)',
        
        # Token manipulation
        r'[\u200B-\u200D\uFEFF]',  # Zero-width characters
        r'[^\w\s\.,\?!;:\-\(\)\[\]\{\}"\'\/\n\r]',  # Unusual chars
        
        # Social engineering
        r'(?i)(emergency|urgent|critical|important).*(tell me|show me|reveal)',
        r'(?i)(help me save|need to know|required for)',
        
        # Template injection
        r'\{\{.*\}\}',  # Jinja/Django
        r'\$\{.*\}',  # JavaScript template literals
        r'<%.*%>',  # EJS/ERB
    ]
    
    # ML-based detection cache
    ML_DETECTION_CACHE_KEY = "ml_injection_detection"
    ML_CONFIDENCE_THRESHOLD = 0.85
    
    def __init__(self):
        """Initialize the sanitizer with ML models."""
        self.ml_classifier = None
        self._load_ml_models()
    
    def _load_ml_models(self):
        """Load ML models for injection detection."""
        try:
            # Load pre-trained model for prompt injection detection
            self.ml_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                device=0 if settings.USE_GPU else -1
            )
            logger.info("ML injection detection model loaded")
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}")
            self.ml_classifier = None
    
    def sanitize_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Sanitize input with multi-layer protection.
        
        Args:
            user_input: Raw user input
            context: Additional context for detection
            
        Returns:
            Sanitized input
            
        Raises:
            PromptInjectionError: If malicious content is detected
        """
        if not user_input:
            return user_input
        
        # Layer 1: Normalize and decode
        normalized = self._normalize_text(user_input)
        
        # Layer 2: Check for encoded content
        decoded = self._detect_and_decode_encodings(normalized)
        if decoded != normalized:
            logger.warning(f"Encoded content detected: {user_input[:100]}...")
            raise PromptInjectionError("Encoded content not allowed")
        
        # Layer 3: Pattern-based detection
        self._check_advanced_patterns(normalized)
        
        # Layer 4: Semantic analysis with ML
        if self.ml_classifier:
            self._ml_detection(normalized, context)
        
        # Layer 5: Contextual analysis
        self._contextual_analysis(normalized, context)
        
        # Layer 6: Sanitize and return
        return self._sanitize_content(normalized)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text to detect evasion attempts."""
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove zero-width characters
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _detect_and_decode_encodings(self, text: str) -> str:
        """Detect and decode various encoding schemes."""
        # Check for base64
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(base64_pattern, text)
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8')
                if self._is_suspicious_content(decoded):
                    return decoded
            except:
                pass
        
        # Check for hex encoding
        hex_pattern = r'(?:0x)?[0-9A-Fa-f]{20,}'
        matches = re.findall(hex_pattern, text)
        for match in matches:
            try:
                clean_hex = match.replace('0x', '')
                if len(clean_hex) % 2 == 0:
                    decoded = binascii.unhexlify(clean_hex).decode('utf-8')
                    if self._is_suspicious_content(decoded):
                        return decoded
            except:
                pass
        
        # Check for URL encoding
        import urllib.parse
        try:
            decoded = urllib.parse.unquote(text)
            if decoded != text and self._is_suspicious_content(decoded):
                return decoded
        except:
            pass
        
        return text
    
    def _is_suspicious_content(self, content: str) -> bool:
        """Check if decoded content contains suspicious patterns."""
        suspicious_keywords = [
            'ignore', 'forget', 'disregard', 'bypass', 'override',
            'system', 'admin', 'developer', 'instruction', 'prompt',
            'hack', 'exploit', 'vulnerability', 'secret'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in suspicious_keywords)
    
    def _check_advanced_patterns(self, text: str):
        """Check for advanced injection patterns."""
        for pattern in self.ADVANCED_PATTERNS:
            if re.search(pattern, text):
                logger.warning(f"Suspicious pattern detected: {pattern}")
                raise PromptInjectionError("Suspicious content pattern detected")
    
    def _ml_detection(self, text: str, context: Optional[Dict[str, Any]]):
        """Use ML to detect subtle injection attempts."""
        # Check cache first
        cache_key = f"{self.ML_DETECTION_CACHE_KEY}:{hashlib.sha256(text.encode()).hexdigest()}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            if cached_result:
                raise PromptInjectionError("ML-based injection detected")
            return
        
        try:
            # Prepare text for classification
            prepared_text = self._prepare_for_ml(text, context)
            
            # Get prediction
            result = self.ml_classifier(prepared_text)
            
            # Check confidence
            if result[0]['score'] > self.ML_CONFIDENCE_THRESHOLD:
                if result[0]['label'] == 'INJECTION':
                    cache.set(cache_key, True, 3600)
                    raise PromptInjectionError("ML-based injection detected")
            
            cache.set(cache_key, False, 3600)
            
        except Exception as e:
            logger.error(f"ML detection failed: {e}")
            # Fail safe - allow if ML fails
    
    def _prepare_for_ml(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """Prepare text for ML classification."""
        # Add context if available
        if context:
            context_str = " | ".join(f"{k}:{v}" for k, v in context.items())
            return f"Context: {context_str}\nInput: {text}"
        return text
    
    def _contextual_analysis(self, text: str, context: Optional[Dict[str, Any]]):
        """Analyze text in context for subtle attacks."""
        if not context:
            return
        
        # Check for attempts to manipulate context
        context_manipulation = [
            'change the context', 'modify the scenario', 'update the context',
            'new context', 'different context', 'alternative context'
        ]
        
        text_lower = text.lower()
        for manipulation in context_manipulation:
            if manipulation in text_lower:
                raise PromptInjectionError("Context manipulation detected")
        
        # Check for privilege escalation attempts
        if 'user' in context and context.get('user_role') != 'admin':
            privilege_patterns = [
                'make me admin', 'elevate privileges', 'grant access',
                'bypass permissions', 'override restrictions'
            ]
            for pattern in privilege_patterns:
                if pattern in text_lower:
                    raise PromptInjectionError("Privilege escalation attempt detected")
    
    def _sanitize_content(self, text: str) -> str:
        """Final sanitization of content."""
        # Remove potentially harmful characters
        # Keep only safe characters
        sanitized = re.sub(r'[^\w\s\.,\?!;:\-\(\)\[\]\{\}"\'\/\n\r@#$%&*+=<>~`|]', '', text)
        
        # Limit length
        max_length = getattr(settings, 'MAX_GENERATOR_INPUT_LENGTH', 2000)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"Input truncated to {max_length} characters")
        
        return sanitized.strip()
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect Personally Identifiable Information in text.
        
        Returns:
            List of detected PII with types and positions
        """
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        }
        
        detected_pii = []
        for pii_type, pattern in pii_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                detected_pii.append({
                    'type': pii_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return detected_pii
    
    def redact_pii(self, text: str) -> str:
        """Redact detected PII from text."""
        pii_list = self.detect_pii(text)
        
        # Redact from end to start to maintain positions
        for pii in sorted(pii_list, key=lambda x: x['start'], reverse=True):
            text = text[:pii['start']] + '[REDACTED]' + text[pii['end']:]
        
        return text


class ContentFilter:
    """
    Enterprise-grade content filtering for outputs.
    """
    
    # Blocked content categories
    BLOCKED_CATEGORIES = [
        'hate_speech',
        'violence',
        'adult_content',
        'illegal_activities',
        'self_harm',
        'medical_advice',
        'legal_advice',
    ]
    
    def __init__(self):
        """Initialize content filter."""
        self.filter_model = None
        self._load_filter_model()
    
    def _load_filter_model(self):
        """Load content filtering model."""
        try:
            # Use perspective API or similar
            from googleapiclient import discovery
            self.filter_model = discovery.build('commentanalyzer', 'v1alpha1')
            logger.info("Content filter model loaded")
        except Exception as e:
            logger.warning(f"Failed to load content filter: {e}")
    
    def filter_content(self, content: str) -> Tuple[bool, List[str]]:
        """
        Filter content for inappropriate material.
        
        Returns:
            Tuple of (is_allowed, list_of_issues)
        """
        issues = []
        
        # Check for blocked patterns
        blocked_patterns = [
            r'(?i)\b(hate|kill|harm|hurt|violence)\b',
            r'(?i)\b(weapon|gun|knife|bomb)\b',
            r'(?i)\b(drug|overdose|suicide)\b',
        ]
        
        for pattern in blocked_patterns:
            if re.search(pattern, content):
                issues.append(f"Blocked pattern detected: {pattern}")
        
        # Use ML filter if available
        if self.filter_model:
            try:
                analyze_request = {
                    'comment': {'text': content},
                    'requestedAttributes': {'TOXICITY': {}}
                }
                response = self.filter_model.comments().analyze(body=analyze_request).execute()
                
                toxicity_score = response['attributeScores']['TOXICITY']['summaryScore']['value']
                if toxicity_score > 0.7:
                    issues.append(f"High toxicity score: {toxicity_score}")
            except Exception as e:
                logger.error(f"Content filtering failed: {e}")
        
        return len(issues) == 0, issues
