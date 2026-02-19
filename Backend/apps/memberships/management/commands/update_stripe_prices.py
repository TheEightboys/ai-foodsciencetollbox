"""
Management command to update the Stripe Price ID for the Pro membership tier.
Usage: python manage.py update_stripe_prices --pro price_xxx

Note: Starter tier was removed. Only Trial (free) and Pro ($25/mo) are active.
"""
from django.core.management.base import BaseCommand
from apps.memberships.models import MembershipTier


class Command(BaseCommand):
    help = 'Update Stripe Price IDs for membership tiers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pro',
            type=str,
            help='Stripe Price ID for Pro tier (e.g., price_0987654321)'
        )

    def handle(self, *args, **options):
        pro_price_id = options.get('pro')
        
        if not pro_price_id:
            self.stdout.write(self.style.ERROR(
                'Please provide the Stripe Price ID using --pro'
            ))
            self.stdout.write('')
            self.stdout.write('Example:')
            self.stdout.write('  python manage.py update_stripe_prices --pro price_0987654321')
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                'IMPORTANT: Price ID must start with "price_" and come from Stripe Dashboard!'
            ))
            self.stdout.write('  - Go to https://dashboard.stripe.com/products')
            self.stdout.write('  - Create a Pro product ($25/month recurring) and copy the Price ID')
            self.stdout.write('  - Also set STRIPE_PRO_PRICE_ID env var on Render for future deployments')
            return
        
        # Validate Price ID format
        invalid_ids = []
        if pro_price_id and not pro_price_id.startswith('price_'):
            invalid_ids.append(f'Pro: {pro_price_id}')
        
        if invalid_ids:
            self.stdout.write(self.style.ERROR(
                'Invalid Price ID format! Stripe Price IDs must start with "price_"'
            ))
            for invalid in invalid_ids:
                self.stdout.write(self.style.ERROR(f'  - {invalid}'))
            self.stdout.write('')
            self.stdout.write('Please get real Price IDs from Stripe Dashboard:')
            self.stdout.write('  https://dashboard.stripe.com/test/products')
            return
        
        updated_count = 0
        
        # Update Pro tier
        if pro_price_id:
            try:
                tier = MembershipTier.objects.get(name='pro')
                tier.stripe_price_id = pro_price_id
                tier.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated Pro tier with Price ID: {pro_price_id}')
                )
                updated_count += 1
            except MembershipTier.DoesNotExist:
                self.stdout.write(self.style.ERROR('Pro tier not found. Run "python manage.py init_tiers" first.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating Pro tier: {e}'))
        
        if updated_count > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} tier(s)'))
            self.stdout.write('')
            self.stdout.write('Current tier configuration:')
            for tier in MembershipTier.objects.filter(is_active=True).order_by('display_order'):
                price_status = tier.stripe_price_id if tier.stripe_price_id else 'NOT CONFIGURED'
                self.stdout.write(f'  {tier.display_name}: {price_status}')

