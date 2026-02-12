"""
Management command to load email templates from client specifications.

Usage:
    python manage.py load_email_templates
"""

from django.core.management.base import BaseCommand
from apps.notifications.models import EmailTemplate


class Command(BaseCommand):
    help = 'Load email templates with content from client specifications'

    def handle(self, *args, **options):
        self.stdout.write('Loading email templates...')
        
        templates = [
            {
                'name': 'welcome',
                'subject': 'Welcome to Food Science Toolbox Teaching Assistant',
                'plain_text_content': """Hi {{ user_name }},

Welcome to Food Science Toolbox Teaching Assistant!

We're excited to have you join our community of educators. You now have access to AI-powered tools to help you create engaging lesson content.

Get started by:
1. Exploring the generators from your dashboard
2. Creating your first lesson starter, learning objectives, or bell ringer
3. Downloading your content in Word or PDF format

If you have any questions, feel free to reach out to us at admin@foodsciencetoolbox.com.

Happy teaching!

Warm regards,
The Food Science Toolbox Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Welcome to Food Science Toolbox Teaching Assistant</h2>
        <p>Hi {{ user_name }},</p>
        <p>Welcome to Food Science Toolbox Teaching Assistant!</p>
        <p>We're excited to have you join our community of educators. You now have access to AI-powered tools to help you create engaging lesson content.</p>
        <p><strong>Get started by:</strong></p>
        <ol>
            <li>Exploring the generators from your dashboard</li>
            <li>Creating your first lesson starter, learning objectives, or bell ringer</li>
            <li>Downloading your content in Word or PDF format</li>
        </ol>
        <p>If you have any questions, feel free to reach out to us at admin@foodsciencetoolbox.com.</p>
        <p>Happy teaching!</p>
        <p>Warm regards,<br><strong>The Food Science Toolbox Team</strong></p>
    </div>
</body>
</html>"""
            },
            {
                'name': 'email_verification',
                'subject': 'Verify Your Email Address for AI Teaching Assistant',
                'plain_text_content': """Hi {{ user_name }},

Thank you for registering with AI Teaching Assistant!

Please click the link below to verify your email address and activate your account:

{{ verification_link }}

This link will expire in 24 hours. If you did not register for an account, please ignore this email.

Warm regards,
The AI Teaching Assistant Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Verify Your Email Address for AI Teaching Assistant</h2>
        <p>Hi {{ user_name }},</p>
        <p>Thank you for registering with AI Teaching Assistant!</p>
        <p>Please click the link below to verify your email address and activate your account:</p>
        <p><a href="{{ verification_link }}" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666; font-size: 12px;">{{ verification_link }}</p>
        <p><strong>This link will expire in 24 hours.</strong> If you did not register for an account, please ignore this email.</p>
        <p>Warm regards,<br><strong>The AI Teaching Assistant Team</strong></p>
    </div>
</body>
</html>"""
            },
            {
                'name': 'password_reset',
                'subject': 'Password Reset Request',
                'plain_text_content': """Hello {{ user_name }},

We received a request to reset your password. If you made this request, use the link below to create a new password:

{{ reset_link }}

If you did not request a reset, you may safely ignore this email.

Thank you,
Food Science Toolbox Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Password Reset Request</h2>
        <p>Hello {{ user_name }},</p>
        <p>We received a request to reset your password. If you made this request, use the link below to create a new password:</p>
        <p><a href="{{ reset_link }}" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666; font-size: 12px;">{{ reset_link }}</p>
        <p>If you did not request a reset, you may safely ignore this email.</p>
        <p>Thank you,<br>Food Science Toolbox Team</p>
    </div>
</body>
</html>"""
            },
            {
                'name': 'upgrade_confirmation',
                'subject': 'Your Pro Subscription Is Active',
                'plain_text_content': """Hello {{ user_name }},

Your account has been successfully upgraded to the Pro plan.

You now have unlimited access to all generators. Your subscription will renew automatically each month unless cancelled.

Thank you for supporting the platform.

Food Science Toolbox Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Your Pro Subscription Is Active</h2>
        <p>Hello {{ user_name }},</p>
        <p>Your account has been successfully upgraded to the Pro plan.</p>
        <p>You now have unlimited access to all generators. Your subscription will renew automatically each month unless cancelled.</p>
        <p>Thank you for supporting the platform.</p>
        <p>Food Science Toolbox Team</p>
    </div>
</body>
</html>"""
            },
            {
                'name': 'limit_reached_trial',
                'subject': 'Free Trial Generations Complete',
                'plain_text_content': """Hello {{ user_name }},
            
You've used all 10 generations in your free 7-day trial.
            
To continue creating content, upgrade to a Starter or Pro plan. Your trial gives you a great taste of what Food Science Toolbox can do for your classroom!
            
Upgrade your plan here: {{ upgrade_url }}
            
Thank you,
Food Science Toolbox Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Free Trial Generations Complete</h2>
        <p>Hello {{ user_name }},</p>
        <p>You've used all 10 generations in your free 7-day trial.</p>
        <p>To continue creating content, upgrade to a Starter or Pro plan. Your trial gives you a great taste of what Food Science Toolbox can do for your classroom!</p>
        <p><a href="{{ upgrade_url }}" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">Upgrade Your Plan</a></p>
        <p>Thank you,<br>Food Science Toolbox Team</p>
    </div>
</body>
</html>"""
            },
            {
                'name': 'limit_reached_starter',
                'subject': 'Monthly Generation Limit Reached',
                'plain_text_content': """Hello {{ user_name }},
            
You have reached your 40-generation monthly limit on the Starter plan.
            
Your count will reset automatically on your next billing cycle. If you would like unlimited access, you may upgrade to the Pro plan at any time.
            
Thank you,
Food Science Toolbox Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Monthly Generation Limit Reached</h2>
        <p>Hello {{ user_name }},</p>
        <p>You have reached your 40-generation monthly limit on the Starter plan.</p>
        <p>Your count will reset automatically on your next billing cycle. If you would like unlimited access, you may upgrade to the Pro plan at any time.</p>
        <p>Thank you,<br>Food Science Toolbox Team</p>
    </div>
</body>
</html>"""
            },
            {
                'name': '90_percent_usage',
                'subject': "Friendly Reminder: You're Almost Out of Your Monthly Generations",
                'plain_text_content': """Hi {{ user_name }},

Just a quick heads-up. You've now used about 90% of your monthly AI generations in Food Science Toolbox Teaching Assistant. We're glad to see you making great use of the tool for your lessons and classroom resources.

If you find that you need more generations each month, you can upgrade your plan at any time to increase your limits and continue creating without interruption.

Upgrade your plan here:

{{ upgrade_url }}

If you have any questions or need help choosing the right plan, feel free to reach out anytime.

Thank you for being part of the Food Science Toolbox community!

Warm regards,

Food Science Toolbox Teaching Assistant""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Friendly Reminder: You're Almost Out of Your Monthly Generations</h2>
        <p>Hi {{ user_name }},</p>
        <p>Just a quick heads-up. You've now used about 90% of your monthly AI generations in Food Science Toolbox Teaching Assistant. We're glad to see you making great use of the tool for your lessons and classroom resources.</p>
        <p>If you find that you need more generations each month, you can upgrade your plan at any time to increase your limits and continue creating without interruption.</p>
        <p><strong>Upgrade your plan here:</strong></p>
        <p><a href="{{ upgrade_url }}" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Upgrade Plan</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all;">{{ upgrade_url }}</p>
        <p>If you have any questions or need help choosing the right plan, feel free to reach out anytime.</p>
        <p>Thank you for being part of the Food Science Toolbox community!</p>
        <p>Warm regards,<br><strong>Food Science Toolbox Teaching Assistant</strong></p>
    </div>
</body>
</html>"""
            },
            {
                'name': 'monthly_reset',
                'subject': 'Your Monthly Generations Have Reset',
                'plain_text_content': """Hello {{ user_name }},

Your monthly usage has been reset. You now have a new set of 40 generations available on your Starter plan.

Thank you for using the platform.

Food Science Toolbox Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">Your Monthly Generations Have Reset</h2>
        <p>Hello {{ user_name }},</p>
        <p>Your monthly usage has been reset. You now have a new set of 40 generations available on your Starter plan.</p>
        <p>Thank you for using the platform.</p>
        <p>Food Science Toolbox Team</p>
    </div>
</body>
</html>"""
            },
            {
                'name': 'support_acknowledgment',
                'subject': 'We Received Your Message',
                'plain_text_content': """Hello {{ user_name }},

Thank you for contacting support. We received your request and will respond as soon as possible.

Thank you,
Food Science Toolbox Team""",
                'html_content': """<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #3b82f6;">We Received Your Message</h2>
        <p>Hello {{ user_name }},</p>
        <p>Thank you for contacting support. We received your request and will respond as soon as possible.</p>
        <p>Thank you,<br>Food Science Toolbox Team</p>
    </div>
</body>
</html>"""
            },
        ]

        for template_data in templates:
            template, created = EmailTemplate.objects.update_or_create(
                name=template_data['name'],
                defaults={
                    'subject': template_data['subject'],
                    'plain_text_content': template_data['plain_text_content'],
                    'html_content': template_data['html_content']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created email template: {template.get_name_display()}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Updated email template: {template.get_name_display()}')
                )

        self.stdout.write(self.style.SUCCESS('Email templates loaded successfully!'))

