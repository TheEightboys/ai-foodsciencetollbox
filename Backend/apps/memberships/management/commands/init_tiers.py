"""
Management command to initialize membership tiers in the database.
Run this command to ensure all required tiers exist.

Usage:
    python manage.py init_tiers
"""
from django.core.management.base import BaseCommand
from apps.memberships.models import MembershipTier


class Command(BaseCommand):
    help = 'Initialize membership tiers in the database'

    def handle(self, *args, **options):
        self.stdout.write('Initializing membership tiers...')
        
        tiers_data = [
            {
                'name': 'trial',
                'display_name': '7-Day Trial',
                'description': 'Free trial with limited generations',
                'monthly_price': 0.00,
                'generation_limit': 10,
                'stripe_price_id': '',  # No Stripe needed for trial
                'is_active': True,
                'display_order': 0,
                'features': [
                    '10 generations',
                    'Word Downloads',
                ]
            },
            {
                'name': 'starter',
                'display_name': 'Starter',
                'description': 'Perfect for teachers getting started with AI-generated content',
                'monthly_price': 12.00,
                'generation_limit': 40,
                'stripe_price_id': '',  # Will need to be set after creating Stripe price
                'is_active': True,
                'display_order': 1,
                'features': [
                    '40 generations per month',
                    'Word Downloads',
                    'Save & Manage Content in Dashboard',
                ]
            },
            {
                'name': 'pro',
                'display_name': 'Pro',
                'description': 'For professional educators who need unlimited content generation',
                'monthly_price': 25.00,
                'generation_limit': None,  # Unlimited
                'stripe_price_id': '',  # Will need to be set after creating Stripe price
                'is_active': True,
                'display_order': 2,
                'features': [
                    'Unlimited generations',
                    'Word Downloads',
                    'Save & Manage Content in Dashboard',
                    'Priority Support',
                    'Early Access to New Tools',
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
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created tier: {tier.display_name} ({tier.name})')
                )
            else:
                # Update existing tier with any missing fields
                updated = False
                # Fields to preserve if already set (don't overwrite user-configured values)
                preserve_fields = ['stripe_price_id']
                
                for key, value in tier_data.items():
                    if key != 'name' and hasattr(tier, key):
                        # Don't overwrite preserved fields if they already have a value
                        if key in preserve_fields and getattr(tier, key, None):
                            continue
                        current_value = getattr(tier, key)
                        if current_value != value:
                            setattr(tier, key, value)
                            updated = True
                
                if updated:
                    tier.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Updated tier: {tier.display_name} ({tier.name})')
                    )
                else:
                    self.stdout.write(
                        f'  Tier already exists: {tier.display_name} ({tier.name})'
                    )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized tiers: {created_count} created, {updated_count} updated'
            )
        )
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('  1. Create Stripe products and prices for Starter and Pro tiers')
        self.stdout.write('  2. Update stripe_price_id for each tier in Django admin')
        self.stdout.write('  3. Test subscription checkout flow')

