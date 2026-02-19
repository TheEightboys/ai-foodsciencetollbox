#!/usr/bin/env python
"""
Standalone script to create membership tiers.
Can be run directly: python create_tiers.py
Or via Django: python manage.py init_tiers
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

from apps.memberships.models import MembershipTier

def create_tiers():
    """Create membership tiers if they don't exist."""
    print("Initializing membership tiers...")
    print("")
    
    tiers_data = [
        {
            'name': 'trial',
            'display_name': '7-Day Trial',
            'description': 'Free trial with limited generations',
            'monthly_price': 0.00,
            'generation_limit': 10,
            'stripe_price_id': '',
            'is_active': True,
            'display_order': 0,
            'features': [
                '10 generations',
                'Word Downloads',
            ]
        },
        {
            'name': 'pro',
            'display_name': 'Pro',
            'description': 'For professional educators who need unlimited content generation',
            'monthly_price': 25.00,
            'generation_limit': None,
            'stripe_price_id': '',
            'is_active': True,
            'display_order': 1,
            'features': [
                'Unlimited generations',
                'Word Downloads',
                'Save & Manage Content in Dashboard',
                'Priority Support',
                'Early Access to New Tools',
                'Food Science Academy Membership',
            ]
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for tier_data in tiers_data:
        tier, created = MembershipTier.objects.get_or_create(
            name=tier_data['name'],
            defaults=tier_data
        )
        
        if created:
            created_count += 1
            print(f"✓ Created tier: {tier.display_name} ({tier.name})")
        else:
            updated = False
            for key, value in tier_data.items():
                if key != 'name' and hasattr(tier, key):
                    current_value = getattr(tier, key)
                    if current_value != value:
                        setattr(tier, key, value)
                        updated = True
            
            if updated:
                tier.save()
                updated_count += 1
                print(f"↻ Updated tier: {tier.display_name} ({tier.name})")
            else:
                print(f"  Tier already exists: {tier.display_name} ({tier.name})")
    
    print("")
    print(f"Successfully initialized tiers: {created_count} created, {updated_count} updated")
    
    # Deactivate starter tier if it exists (no longer offered)
    deactivated = MembershipTier.objects.filter(name='starter', is_active=True).update(is_active=False)
    if deactivated:
        print(f"↻ Deactivated Starter tier (no longer offered — hidden from users)")
    
    print("")
    print("Next steps:")
    print("  1. Create a Stripe product and price for the Pro tier ($25/mo)")
    print("  2. Set STRIPE_PRO_PRICE_ID env var on Render (starts with 'price_')")
    print("  3. Run: python manage.py update_stripe_prices --pro <price_id>")
    print("  4. Set STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET on Render")
    print("  5. Test subscription checkout flow")

if __name__ == '__main__':
    try:
        create_tiers()
    except Exception as e:
        print(f"Error creating tiers: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

