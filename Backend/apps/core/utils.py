import secrets
import string
from django.utils.text import slugify


def generate_random_token(length=32):
    """
    Generate a random token string.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_slug(text, model_class, max_length=50):
    """
    Generate a unique slug for a model instance.
    """
    slug = slugify(text)[:max_length]
    unique_slug = slug
    num = 1
    
    while model_class.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{slug}-{num}"
        num += 1
        
    return unique_slug


def calculate_reading_time(text, words_per_minute=200):
    """
    Calculate estimated reading time for text content.
    """
    words = len(text.split())
    minutes = words / words_per_minute
    return round(minutes)


def format_currency(amount, currency='USD'):
    """
    Format currency amount for display.
    """
    if currency == 'USD':
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"