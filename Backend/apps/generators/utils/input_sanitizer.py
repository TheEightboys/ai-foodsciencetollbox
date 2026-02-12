"""
Input sanitization and validation utilities.
Prevents prompt injection and ensures safe input to LLMs.
"""

import re
from typing import Optional, List
from django.conf import settings
from .exceptions import PromptInjectionError


class InputSanitizer:
    """Sanitizes user inputs to prevent prompt injection attacks."""
    
    # Patterns that indicate prompt injection attempts
    SUSPICIOUS_PATTERNS = [
        r'(?i)(ignore|forget|disregard).*(previous|above|earlier).*(instruction|prompt|context)',
        r'(?i)(instead|rather|alternatively).*(generate|create|write)',
        r'(?i)(system|developer|admin).*(instruction|directive|command)',
        r'(?i)(act|behave|pretend).*(as|like).*(system|admin|developer)',
        r'(?i)(override|bypass|circumvent).*(restriction|filter|rule)',
        r'(?i)(jailbreak|jail.break|jail-break)',
        r'(?i)(translate|convert|explain).*(previous|above).*(to|into)',
        r'(?i)(\{\{.*\}\}|\[.*\]|\<.*\>)',  # Template injection patterns
        r'(?i)(base64|hex|encode|decode)',
        r'(?i)(json|yaml|xml).*(parse|decode)',
        r'(?i)(eval|exec|function|return)',
        r'(?i)(__import__|__builtins__|__globals__)',
    ]
    
    # Maximum allowed input length
    MAX_INPUT_LENGTH = getattr(settings, 'MAX_GENERATOR_INPUT_LENGTH', 2000)
    
    # Blocked words list
    BLOCKED_WORDS = [
        'password', 'token', 'secret', 'key', 'credential',
        'hack', 'exploit', 'vulnerability', 'bypass',
        'sqlmap', 'nmap', 'metasploit', 'burp',
    ]
    
    @classmethod
    def sanitize_input(cls, user_input: str, field_name: str = "input") -> str:
        """
        Sanitize user input to prevent prompt injection.
        
        Args:
            user_input: Raw user input
            field_name: Name of the field for error reporting
            
        Returns:
            Sanitized input
            
        Raises:
            PromptInjectionError: If suspicious content is detected
        """
        if not user_input:
            return user_input
        
        # Check input length
        if len(user_input) > cls.MAX_INPUT_LENGTH:
            raise PromptInjectionError(
                f"{field_name} exceeds maximum length of {cls.MAX_INPUT_LENGTH} characters"
            )
        
        # Convert to lowercase for pattern matching
        input_lower = user_input.lower()
        
        # Check for blocked words
        for word in cls.BLOCKED_WORDS:
            if word in input_lower:
                raise PromptInjectionError(
                    f"{field_name} contains prohibited content"
                )
        
        # Check for suspicious patterns
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, user_input):
                raise PromptInjectionError(
                    f"{field_name} appears to contain suspicious content"
                )
        
        # Remove potentially harmful characters
        # Keep only safe characters: letters, numbers, punctuation, spaces
        sanitized = re.sub(r'[^\w\s\.,\?!;:\-\(\)\[\]\{\}"\'\/\n\r]', '', user_input)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    @classmethod
    def validate_json_input(cls, json_data: dict, required_fields: Optional[List[str]] = None) -> dict:
        """
        Validate JSON input for APIs.
        
        Args:
            json_data: Dictionary to validate
            required_fields: List of required field names
            
        Returns:
            Validated dictionary
            
        Raises:
            PromptInjectionError: If validation fails
        """
        if not isinstance(json_data, dict):
            raise PromptInjectionError("Invalid input format")
        
        # Check required fields
        if required_fields:
            missing_fields = [field for field in required_fields if field not in json_data]
            if missing_fields:
                raise PromptInjectionError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Sanitize all string values
        sanitized_data = {}
        for key, value in json_data.items():
            if isinstance(value, str):
                sanitized_data[key] = cls.sanitize_input(value, key)
            elif isinstance(value, (list, dict)):
                # Recursively sanitize nested structures
                sanitized_data[key] = cls._sanitize_nested(value)
            else:
                sanitized_data[key] = value
        
        return sanitized_data
    
    @classmethod
    def _sanitize_nested(cls, data):
        """Recursively sanitize nested data structures."""
        if isinstance(data, str):
            return cls.sanitize_input(data)
        elif isinstance(data, list):
            return [cls._sanitize_nested(item) for item in data]
        elif isinstance(data, dict):
            return {k: cls._sanitize_nested(v) for k, v in data.items()}
        else:
            return data
