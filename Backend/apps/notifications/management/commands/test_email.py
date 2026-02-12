"""
Management command to test email sending functionality.
Usage: python manage.py test_email <email_address>
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from apps.notifications.services import EmailService


class Command(BaseCommand):
    help = 'Test email sending functionality by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test email to'
        )
        parser.add_argument(
            '--method',
            type=str,
            choices=['direct', 'service'],
            default='direct',
            help='Method to use: direct (send_mail) or service (EmailService)'
        )

    def handle(self, *args, **options):
        email = options['email']
        method = options['method']
        
        self.stdout.write(self.style.WARNING(f'Testing email configuration...'))
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write('')
        
        if method == 'direct':
            self.stdout.write(self.style.WARNING(f'Sending test email to {email} using send_mail...'))
            try:
                send_mail(
                    'Test Email from Food Science Toolbox',
                    'This is a test email to verify that email sending is working correctly.\n\n'
                    'If you received this email, your email configuration is working properly!',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Test email sent successfully to {email}'))
                self.stdout.write(self.style.SUCCESS('Please check the inbox (and spam folder) for the test email.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to send test email: {e}'))
                self.stdout.write(self.style.ERROR('Please check your email configuration in environment variables.'))
                raise CommandError(f'Email sending failed: {e}')
        else:
            # Try using EmailService (requires a user object)
            self.stdout.write(self.style.WARNING(f'Sending test email to {email} using EmailService...'))
            try:
                from apps.accounts.models import User
                # Try to get or create a test user
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': 'Test',
                        'last_name': 'User',
                        'is_active': True
                    }
                )
                
                # Send a simple test email using send_mail directly (EmailService requires templates)
                send_mail(
                    'Test Email from Food Science Toolbox',
                    f'Hi {user.first_name},\n\n'
                    'This is a test email to verify that email sending is working correctly.\n\n'
                    'If you received this email, your email configuration is working properly!',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Test email sent successfully to {email}'))
                self.stdout.write(self.style.SUCCESS('Please check the inbox (and spam folder) for the test email.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed to send test email: {e}'))
                self.stdout.write(self.style.ERROR('Please check your email configuration in environment variables.'))
                raise CommandError(f'Email sending failed: {e}')

