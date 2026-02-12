from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.conf import settings
from .models import EmailTemplate, EmailLog
from .models import EmailTemplate, EmailLog


class EmailService:
    """
    Service to handle sending emails with templates.
    """

    @staticmethod
    def send_email_with_template(user, template_name, context=None):
        """
        Send an email to a user using a predefined template.
        Returns True if sent successfully, False otherwise.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if context is None:
            context = {}
            
        try:
            # Get the email template
            template = EmailTemplate.objects.get(name=template_name)
        except EmailTemplate.DoesNotExist:
            # Log error but don't fail - let caller handle fallback
            logger.warning(f"Email template '{template_name}' not found for user {user.email}")
            EmailLog.objects.create(
                user=user,
                subject=f"Template {template_name} not found",
                recipient=user.email,
                status='failed',
                plain_text_content=f"Template {template_name} not found",
                error_message=f"Email template '{template_name}' does not exist"
            )
            # Raise exception so caller can use fallback
            raise EmailTemplate.DoesNotExist(f"Template '{template_name}' not found")
        
        # Render the template with context
        subject_template = Template(template.subject)
        plain_text_template = Template(template.plain_text_content)
        html_template = Template(template.html_content)
        
        context_dict = {
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'AI Teaching Assistant'),
            'frontend_url': getattr(settings, 'FRONTEND_URL', ''),
        }
        context_dict.update(context)
        
        ctx = Context(context_dict)
        
        subject = subject_template.render(ctx)
        plain_text_content = plain_text_template.render(ctx)
        html_content = html_template.render(ctx)
        
        # Send the email
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            # Log the email
            EmailLog.objects.create(
                user=user,
                template=template,
                subject=subject,
                recipient=user.email,
                status='sent',
                plain_text_content=plain_text_content,
                html_content=html_content
            )
            
            return True
        except Exception as e:
            # Log the error
            EmailLog.objects.create(
                user=user,
                template=template,
                subject=subject,
                recipient=user.email,
                status='failed',
                plain_text_content=plain_text_content,
                html_content=html_content,
                error_message=str(e)
            )
            return False

    @staticmethod
    def send_welcome_email(user):
        """
        Send a welcome email to a new user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Try to use template if it exists
        context = {
            'user_name': user.first_name or user.email.split('@')[0]
        }
        try:
            result = EmailService.send_email_with_template(user, 'welcome', context)
            if result:
                logger.info(f"Welcome email sent successfully to {user.email}")
                return result
        except Exception as template_error:
            logger.warning(f"Welcome email template failed for {user.email}: {template_error}. Using fallback.")
        
        # Fallback: send direct email if template doesn't exist or fails
        from django.core.mail import send_mail
        
        user_name = user.first_name or user.email.split('@')[0]
        subject = "Welcome to Food Science Toolbox Teaching Assistant"
        message = f"""Hi {user_name},

Welcome to Food Science Toolbox Teaching Assistant!

We're excited to have you join our community of educators. You now have access to AI-powered tools to help you create engaging lesson content.

Get started by:
1. Exploring the generators from your dashboard
2. Creating your first lesson starter, learning objectives, or bell ringer
3. Downloading your content in Word or PDF format

If you have any questions, feel free to reach out to us at admin@foodsciencetoolbox.com.

Happy teaching!

Warm regards,
The Food Science Toolbox Team"""
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Welcome email sent successfully (fallback) to {user.email}")
            return True
        except Exception as mail_error:
            logger.error(f"Failed to send welcome email to {user.email}: {mail_error}", exc_info=True)
            return False

    @staticmethod
    def send_password_reset_email(user, reset_url):
        """
        Send a password reset email to a user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        context = {
            'reset_link': reset_url,
            'reset_url': reset_url,  # Support both variable names
            'user_name': user.first_name or user.email.split('@')[0]
        }
        
        # Try to use template if it exists, otherwise send direct email
        try:
            result = EmailService.send_email_with_template(user, 'password_reset', context)
            if result:
                logger.info(f"Password reset email sent successfully to {user.email}")
                return result
        except Exception as template_error:
            logger.warning(f"Password reset template failed for {user.email}: {template_error}. Using fallback.")
            from django.core.mail import send_mail
            
            subject = "Password Reset Request"
            message = f"""Hello {context['user_name']},

We received a request to reset your password. If you made this request, use the link below to create a new password:

{reset_url}

If you did not request a reset, you may safely ignore this email.

Thank you,
Food Science Toolbox Team"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Password reset email sent successfully (fallback) to {user.email}")
                return True
            except Exception as mail_error:
                logger.error(f"Failed to send password reset email to {user.email}: {mail_error}", exc_info=True)
                return False

    @staticmethod
    def send_upgrade_confirmation_email(user, tier_name):
        """
        Send an upgrade confirmation email to a user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        context = {
            'tier_name': tier_name,
            'user_name': user.first_name or user.email.split('@')[0]
        }
        
        # Try to use template if it exists, otherwise send direct email
        try:
            result = EmailService.send_email_with_template(user, 'upgrade_confirmation', context)
            if result:
                logger.info(f"Upgrade confirmation email sent successfully to {user.email}")
                return result
        except Exception as template_error:
            logger.warning(f"Upgrade confirmation template failed for {user.email}: {template_error}. Using fallback.")
            from django.core.mail import send_mail
            
            subject = "Your Pro Subscription Is Active"
            message = f"""Hello {context['user_name']},

Your account has been successfully upgraded to the Pro plan.

You now have unlimited access to all generators. Your subscription will renew automatically each month unless cancelled.

Thank you for supporting the platform.

Food Science Toolbox Team"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Upgrade confirmation email sent successfully (fallback) to {user.email}")
                return True
            except Exception as mail_error:
                logger.error(f"Failed to send upgrade confirmation email to {user.email}: {mail_error}", exc_info=True)
                return False

    @staticmethod
    def send_limit_reached_email(user):
        """
        Send a generation limit reached email to a user.
        Uses different templates for trial vs starter users.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Get user's membership tier to determine which template to use
        try:
            from apps.memberships.models import UserMembership
            membership = UserMembership.objects.select_related('tier').get(user=user)
            tier_name = membership.tier.name.lower() if membership.tier else 'trial'
        except Exception:
            tier_name = 'trial'  # Default to trial if membership not found
        
        # Get frontend URL for upgrade link
        frontend_url = settings.FRONTEND_URL
        upgrade_url = f"{frontend_url}/pricing"
        
        context = {
            'user_name': user.first_name or user.email.split('@')[0],
            'upgrade_url': upgrade_url
        }
        
        # Determine template name based on tier
        if tier_name == 'trial':
            template_name = 'limit_reached_trial'
        else:
            template_name = 'limit_reached_starter'
        
        # Try to use template if it exists, otherwise send direct email
        try:
            result = EmailService.send_email_with_template(user, template_name, context)
            if result:
                logger.info(f"Limit reached email sent successfully to {user.email} (tier: {tier_name})")
                return result
        except Exception as template_error:
            logger.warning(f"Limit reached template '{template_name}' failed for {user.email}: {template_error}. Using fallback.")
            from django.core.mail import send_mail
            
            # Fallback messages based on tier
            if tier_name == 'trial':
                subject = "Free Trial Generations Complete"
                message = f"""Hello {context['user_name']},
                
You've used all 10 generations in your free 7-day trial.
                
To continue creating content, upgrade to a Starter or Pro plan. Your trial gives you a great taste of what Food Science Toolbox can do for your classroom!
                
Upgrade your plan here: {upgrade_url}
                
Thank you,
Food Science Toolbox Team"""
            else:
                subject = "Monthly Generation Limit Reached"
                message = f"""Hello {context['user_name']},
                
You have reached your 40-generation monthly limit on the Starter plan.
                
Your count will reset automatically on your next billing cycle. If you would like unlimited access, you may upgrade to the Pro plan at any time.
                
Thank you,
Food Science Toolbox Team"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Limit reached email sent successfully (fallback) to {user.email}")
                return True
            except Exception as mail_error:
                logger.error(f"Failed to send limit reached email to {user.email}: {mail_error}", exc_info=True)
                return False
    
    @staticmethod
    def send_90_percent_usage_email(user, upgrade_url=None):
        """
        Send an email when user reaches 90% of their generation limit.
        """
        from django.conf import settings
        
        if upgrade_url is None:
            frontend_url = settings.FRONTEND_URL
            upgrade_url = f"{frontend_url}/pricing"
        
        context = {
            'upgrade_url': upgrade_url,
            'user_name': user.first_name or user.email.split('@')[0]
        }
        
        # Try to use template if it exists, otherwise send direct email
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            result = EmailService.send_email_with_template(user, '90_percent_usage', context)
            if result:
                logger.info(f"90% usage email sent successfully to {user.email}")
                return result
        except Exception as template_error:
            logger.warning(f"90% usage template failed for {user.email}: {template_error}. Using fallback.")
            from django.core.mail import send_mail
            
            subject = "Friendly Reminder: You're Almost Out of Your Monthly Generations"
            message = f"""Hi {context['user_name']},

Just a quick heads-up. You've now used about 90% of your monthly AI generations in Food Science Toolbox Teaching Assistant. We're glad to see you making great use of the tool for your lessons and classroom resources.

If you find that you need more generations each month, you can upgrade your plan at any time to increase your limits and continue creating without interruption.

Upgrade your plan here:
{upgrade_url}

If you have any questions or need help choosing the right plan, feel free to reach out anytime.

Thank you for being part of the Food Science Toolbox community!

Warm regards,
Food Science Toolbox Teaching Assistant"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"90% usage email sent successfully (fallback) to {user.email}")
                return True
            except Exception as mail_error:
                logger.error(f"Failed to send 90% usage email to {user.email}: {mail_error}", exc_info=True)
                return False

    @staticmethod
    def send_monthly_reset_email(user):
        """
        Send a monthly usage reset email to a user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        context = {
            'user_name': user.first_name or user.email.split('@')[0]
        }
        
        # Try to use template if it exists, otherwise send direct email
        try:
            result = EmailService.send_email_with_template(user, 'monthly_reset', context)
            if result:
                logger.info(f"Monthly reset email sent successfully to {user.email}")
                return result
        except Exception as template_error:
            logger.warning(f"Monthly reset template failed for {user.email}: {template_error}. Using fallback.")
            from django.core.mail import send_mail
            
            subject = "Your Monthly Generations Have Reset"
            message = f"""Hello {context['user_name']},

Your monthly usage has been reset. You now have a new set of 40 generations available on your Starter plan.

Thank you for using the platform.

Food Science Toolbox Team"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Monthly reset email sent successfully (fallback) to {user.email}")
                return True
            except Exception as mail_error:
                logger.error(f"Failed to send monthly reset email to {user.email}: {mail_error}", exc_info=True)
                return False

    @staticmethod
    def send_email_verification(user, verification_link):
        """
        Send an email verification email to a user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        context = {
            'verification_link': verification_link,
            'user_name': user.first_name or user.email.split('@')[0]
        }
        
        # Try to use template if it exists, otherwise send direct email
        try:
            result = EmailService.send_email_with_template(user, 'email_verification', context)
            if result:
                logger.info(f"Email verification sent successfully to {user.email}")
                return result
            else:
                logger.warning(f"Email verification template send returned False for {user.email}. Using fallback.")
        except Exception as template_error:
            # Fallback: send direct email if template doesn't exist
            logger.warning(f"Email verification template failed for {user.email}: {template_error}. Using fallback.")
            from django.core.mail import send_mail
            
            subject = "Verify Your Email Address for AI Teaching Assistant"
            message = f"""Hi {context['user_name']},

Thank you for registering with AI Teaching Assistant!

Please click the link below to verify your email address and activate your account:

{verification_link}

This link will expire in 24 hours. If you did not register for an account, please ignore this email.

Warm regards,
The AI Teaching Assistant Team"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Email verification sent successfully (fallback) to {user.email}")
                return True
            except Exception as mail_error:
                logger.error(f"Failed to send email verification to {user.email}: {mail_error}", exc_info=True)
                return False

    @staticmethod
    def send_support_acknowledgment(user):
        """
        Send a support ticket acknowledgment email to a user.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        context = {
            'user_name': user.first_name or user.email.split('@')[0]
        }
        
        # Try to use template if it exists, otherwise send direct email
        try:
            result = EmailService.send_email_with_template(user, 'support_acknowledgment', context)
            if result:
                logger.info(f"Support acknowledgment email sent successfully to {user.email}")
                return result
        except Exception as template_error:
            logger.warning(f"Support acknowledgment template failed for {user.email}: {template_error}. Using fallback.")
            from django.core.mail import send_mail
            
            subject = "We Received Your Message"
            message = f"""Hello {context['user_name']},

Thank you for contacting support. We received your request and will respond as soon as possible.

Thank you,
Food Science Toolbox Team"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Support acknowledgment email sent successfully (fallback) to {user.email}")
                return True
            except Exception as mail_error:
                logger.error(f"Failed to send support acknowledgment email to {user.email}: {mail_error}", exc_info=True)
                return False