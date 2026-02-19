#!/usr/bin/env python
"""
Quick script to set the Stripe Price ID for the Pro subscription tier.
Starter tier has been removed; only Trial (free) and Pro ($25/mo) are active.

Usage:
    python setup_stripe_test_prices.py --pro price_xxx

Or set via environment variable:
    export STRIPE_PRO_PRICE_ID=price_xxx
    python setup_stripe_test_prices.py
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
import argparse


def setup_stripe_prices(pro_price_id=None):
    """Set Stripe Price ID for the Pro membership tier."""
    
    # Get from environment if not provided
    if not pro_price_id:
        pro_price_id = os.environ.get('STRIPE_PRO_PRICE_ID', '')
    
    if not pro_price_id:
        print("=" * 60)
        print("Stripe Price ID Setup (Pro Tier)")
        print("=" * 60)
        print("")
        print("You need to provide the Stripe Price ID for the Pro tier.")
        print("")
        print("Option 1: Via command line argument")
        print("  python setup_stripe_test_prices.py --pro price_xxx")
        print("")
        print("Option 2: Via environment variable")
        print("  export STRIPE_PRO_PRICE_ID=price_xxx")
        print("  python setup_stripe_test_prices.py")
        print("")
        print("Option 3: Via Django management command")
        print("  python manage.py update_stripe_prices --pro price_xxx")
        print("")
        print("To get your Stripe Price ID:")
        print("  1. Go to https://dashboard.stripe.com/products")
        print("  2. Create a product for Pro ($25/month recurring)")
        print("  3. Copy the Price ID (starts with 'price_')")
        print("  4. Also add it as STRIPE_PRO_PRICE_ID env var on Render")
        print("")
        return False
    
    updated = []
    
    # Update Pro tier
    if pro_price_id:
        try:
            tier = MembershipTier.objects.get(name='pro')
            old_price_id = tier.stripe_price_id
            tier.stripe_price_id = pro_price_id.strip()
            tier.save()
            print(f"✓ Updated Pro tier:")
            print(f"  Old: {old_price_id or '(empty)'}")
            print(f"  New: {tier.stripe_price_id}")
            updated.append('Pro')
        except MembershipTier.DoesNotExist:
            print("✗ Error: Pro tier not found. Run 'python manage.py init_tiers' first.")
        except Exception as e:
            print(f"✗ Error updating Pro tier: {e}")
    
    if updated:
        print("")
        print("=" * 60)
        print(f"Successfully updated {len(updated)} tier(s): {', '.join(updated)}")
        print("=" * 60)
        print("")
        print("Current tier configuration:")
        for tier in MembershipTier.objects.filter(is_active=True).order_by('display_order'):
            price_status = tier.stripe_price_id if tier.stripe_price_id else '❌ NOT CONFIGURED'
            print(f"  {tier.display_name:20} {price_status}")
        print("")
        return True
    
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set Stripe Price ID for Pro tier')
    parser.add_argument('--pro', type=str, help='Stripe Price ID for Pro tier (starts with price_)')
    
    args = parser.parse_args()
    
    success = setup_stripe_prices(
        pro_price_id=args.pro
    )
    
    sys.exit(0 if success else 1)

