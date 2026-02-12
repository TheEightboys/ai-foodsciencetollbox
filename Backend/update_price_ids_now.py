#!/usr/bin/env python
"""
Direct script to update Stripe Price IDs immediately.
This bypasses any admin form issues.
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
    sys.exit(1)

from apps.memberships.models import MembershipTier

# Your Stripe Price IDs
STARTER_PRICE_ID = 'price_1SeQc3PwNxCKLfDfdpzjcyiZ'
PRO_PRICE_ID = 'price_1SeQgIPwNxCKLfDfS8jECteZ'

print("=" * 60)
print("Updating Stripe Price IDs")
print("=" * 60)
print("")

# Update Starter
try:
    starter = MembershipTier.objects.get(name='starter')
    old_starter = starter.stripe_price_id
    starter.stripe_price_id = STARTER_PRICE_ID
    starter.save()
    print(f"✓ Starter tier updated:")
    print(f"  Old: {old_starter or '(empty)'}")
    print(f"  New: {starter.stripe_price_id}")
except MembershipTier.DoesNotExist:
    print("✗ ERROR: Starter tier not found!")
except Exception as e:
    print(f"✗ ERROR updating Starter: {e}")

print("")

# Update Pro
try:
    pro = MembershipTier.objects.get(name='pro')
    old_pro = pro.stripe_price_id
    pro.stripe_price_id = PRO_PRICE_ID
    pro.save()
    print(f"✓ Pro tier updated:")
    print(f"  Old: {old_pro or '(empty)'}")
    print(f"  New: {pro.stripe_price_id}")
except MembershipTier.DoesNotExist:
    print("✗ ERROR: Pro tier not found!")
except Exception as e:
    print(f"✗ ERROR updating Pro: {e}")

print("")
print("=" * 60)
print("Verification:")
print("=" * 60)

# Verify
for tier in MembershipTier.objects.filter(is_active=True).order_by('display_order'):
    price_id = tier.stripe_price_id
    status = "✓ CONFIGURED" if price_id else "✗ NOT CONFIGURED"
    print(f"  {tier.display_name:20} {status}")
    if price_id:
        print(f"    Price ID: {price_id}")

print("")
print("Done! Price IDs have been updated.")

