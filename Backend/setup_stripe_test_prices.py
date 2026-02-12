#!/usr/bin/env python
"""
Quick script to set test Stripe Price IDs for development/testing.
This uses Stripe test mode Price IDs that you can create in your Stripe Dashboard.

Usage:
    python setup_stripe_test_prices.py --starter price_test_xxx --pro price_test_yyy

Or set them via environment variables:
    export STRIPE_STARTER_PRICE_ID=price_test_xxx
    export STRIPE_PRO_PRICE_ID=price_test_yyy
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


def setup_stripe_prices(starter_price_id=None, pro_price_id=None):
    """Set Stripe Price IDs for membership tiers."""
    
    # Get from environment if not provided
    if not starter_price_id:
        starter_price_id = os.environ.get('STRIPE_STARTER_PRICE_ID', '')
    if not pro_price_id:
        pro_price_id = os.environ.get('STRIPE_PRO_PRICE_ID', '')
    
    if not starter_price_id and not pro_price_id:
        print("=" * 60)
        print("Stripe Price ID Setup")
        print("=" * 60)
        print("")
        print("You need to provide Stripe Price IDs for Starter and Pro tiers.")
        print("")
        print("Option 1: Via command line arguments")
        print("  python setup_stripe_test_prices.py --starter price_test_xxx --pro price_test_yyy")
        print("")
        print("Option 2: Via environment variables")
        print("  export STRIPE_STARTER_PRICE_ID=price_test_xxx")
        print("  export STRIPE_PRO_PRICE_ID=price_test_yyy")
        print("  python setup_stripe_test_prices.py")
        print("")
        print("Option 3: Via Django management command")
        print("  python manage.py update_stripe_prices --starter price_test_xxx --pro price_test_yyy")
        print("")
        print("To get your Stripe Price IDs:")
        print("  1. Go to https://dashboard.stripe.com/products")
        print("  2. Create products for Starter ($12/month) and Pro ($25/month)")
        print("  3. Copy the Price IDs (they start with 'price_')")
        print("")
        return False
    
    updated = []
    
    # Update Starter tier
    if starter_price_id:
        try:
            tier = MembershipTier.objects.get(name='starter')
            old_price_id = tier.stripe_price_id
            tier.stripe_price_id = starter_price_id.strip()
            tier.save()
            print(f"✓ Updated Starter tier:")
            print(f"  Old: {old_price_id or '(empty)'}")
            print(f"  New: {tier.stripe_price_id}")
            updated.append('Starter')
        except MembershipTier.DoesNotExist:
            print("✗ Error: Starter tier not found. Run 'python manage.py init_tiers' first.")
        except Exception as e:
            print(f"✗ Error updating Starter tier: {e}")
    
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
    parser = argparse.ArgumentParser(description='Set Stripe Price IDs for membership tiers')
    parser.add_argument('--starter', type=str, help='Stripe Price ID for Starter tier')
    parser.add_argument('--pro', type=str, help='Stripe Price ID for Pro tier')
    
    args = parser.parse_args()
    
    success = setup_stripe_prices(
        starter_price_id=args.starter,
        pro_price_id=args.pro
    )
    
    sys.exit(0 if success else 1)

