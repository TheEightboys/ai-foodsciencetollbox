"""
Management command to create a superuser non-interactively.
Usage: python manage.py create_superuser
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create a superuser with predefined credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@foodsciencetoolbox.com',
            help='Email address for the superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin',
            help='Password for the superuser'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='First name for the superuser'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name for the superuser'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        
        self.stdout.write(f'Creating superuser: {email}')
        self.stdout.write('')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Update to superuser if not already
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.set_password(password)
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated existing user to superuser: {email}')
                )
            else:
                # Update password and name
                user.set_password(password)
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated password for existing superuser: {email}')
                )
        else:
            # Create new superuser
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created new superuser: {email}')
            )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Superuser credentials:'))
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING(
            'IMPORTANT: Change the password after first login for security!'
        ))
        self.stdout.write('')
        self.stdout.write('You can now access Django admin at: /admin/')

