"""
Management command to update membership tier pricing.

Usage:
    python manage.py update_pricing
"""

from django.core.management.base import BaseCommand
from apps.memberships.models import MembershipTier


class Command(BaseCommand):
    help = 'Update membership tier pricing to match client specifications'

    def handle(self, *args, **options):
        self.stdout.write('Updating membership tier pricing...')
        
        # Update Starter tier
        try:
            starter = MembershipTier.objects.get(name='starter')
            starter.monthly_price = 12.00
            starter.generation_limit = 40
            starter.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated Starter tier: ${starter.monthly_price}/month, {starter.generation_limit} generations')
            )
        except MembershipTier.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Starter tier not found. Please create it in admin.')
            )
        
        # Update Pro tier
        try:
            pro = MembershipTier.objects.get(name='pro')
            pro.monthly_price = 25.00
            pro.generation_limit = None  # Unlimited
            pro.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated Pro tier: ${pro.monthly_price}/month, unlimited generations')
            )
        except MembershipTier.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Pro tier not found. Please create it in admin.')
            )
        
        self.stdout.write(self.style.SUCCESS('Pricing update completed!'))

