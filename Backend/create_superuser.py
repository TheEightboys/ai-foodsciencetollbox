#!/usr/bin/env python
"""
Standalone script to create a superuser.
Can be run directly: python create_superuser.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print("Trying with development settings...")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.development'
    django.setup()

from apps.accounts.models import User

def create_superuser():
    """Create superuser if it doesn't exist."""
    email = 'admin@foodsciencetoolbox.com'
    password = 'Admin'
    first_name = 'Admin'
    last_name = 'User'
    
    print(f"Creating superuser: {email}")
    print("")
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        # Update to superuser if not already
        if not user.is_superuser:
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.set_password(password)
            user.save()
            print(f"✓ Updated existing user to superuser: {email}")
        else:
            # Update password
            user.set_password(password)
            user.save()
            print(f"✓ Updated password for existing superuser: {email}")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        print(f"✓ Created new superuser: {email}")
    
    print("")
    print("Superuser credentials:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print("")
    print("You can now access Django admin at: /admin/")
    print("IMPORTANT: Change the password after first login for security!")

if __name__ == '__main__':
    try:
        create_superuser()
    except Exception as e:
        print(f"Error creating superuser: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

