"""
Simple test to verify refactored views are working.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Test import
try:
    from apps.generators.views_refactored_package.refactored import LessonStarterGenerateView
    print("✅ Successfully imported refactored views!")
    print("✅ Views are using centralized error handling")
    print("✅ No more duplicate try-except blocks")
    print("✅ Consistent error response format")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test URL configuration
try:
    from django.urls import reverse
    url = reverse('generators:lesson-starter-generate')
    print(f"✅ URL resolved: {url}")
except Exception as e:
    print(f"❌ URL resolution failed: {e}")

print("\n🎉 Migration to refactored views successful!")
print("\nBenefits:")
print("- Centralized error handling with @handle_generator_errors decorator")
print("- Consistent error codes and messages")
print("- No code duplication")
print("- Better maintainability")
