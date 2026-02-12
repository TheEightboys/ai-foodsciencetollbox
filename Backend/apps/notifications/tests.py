from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import EmailTemplate, EmailLog
from .services import EmailService

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create email template
        self.email_template = EmailTemplate.objects.create(
            name='welcome',
            subject='Welcome to our platform',
            plain_text_content='Welcome {{ user.first_name }}!',
            html_content='<h1>Welcome {{ user.first_name }}!</h1>'
        )

    def test_email_template_creation(self):
        self.assertEqual(self.email_template.name, 'welcome')
        self.assertEqual(self.email_template.subject, 'Welcome to our platform')
        self.assertEqual(self.email_template.plain_text_content, 'Welcome {{ user.first_name }}!')
        self.assertEqual(self.email_template.html_content, '<h1>Welcome {{ user.first_name }}!</h1>')

    def test_email_log_creation(self):
        email_log = EmailLog.objects.create(
            user=self.user,
            template=self.email_template,
            subject='Welcome to our platform',
            recipient=self.user.email,
            status='sent',
            plain_text_content='Welcome Test!',
            html_content='<h1>Welcome Test!</h1>'
        )
        
        self.assertEqual(email_log.user, self.user)
        self.assertEqual(email_log.template, self.email_template)
        self.assertEqual(email_log.subject, 'Welcome to our platform')
        self.assertEqual(email_log.recipient, self.user.email)
        self.assertEqual(email_log.status, 'sent')
        self.assertEqual(email_log.plain_text_content, 'Welcome Test!')
        self.assertEqual(email_log.html_content, '<h1>Welcome Test!</h1>')


class NotificationServiceTest(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create email template
        self.email_template = EmailTemplate.objects.create(
            name='welcome',
            subject='Welcome to our platform',
            plain_text_content='Welcome {{ user.first_name }}!',
            html_content='<h1>Welcome {{ user.first_name }}!</h1>'
        )

    @patch('apps.notifications.services.EmailMultiAlternatives.send')
    def test_send_email_with_template_success(self, mock_send):
        # Mock successful email sending
        mock_send.return_value = None
        
        # Send email
        result = EmailService.send_email_with_template(self.user, 'welcome')
        
        # Check result
        self.assertTrue(result)
        
        # Check that email log was created
        self.assertEqual(EmailLog.objects.count(), 1)
        email_log = EmailLog.objects.first()
        self.assertEqual(email_log.user, self.user)
        self.assertEqual(email_log.status, 'sent')
        
    @patch('apps.notifications.services.EmailMultiAlternatives.send')
    def test_send_email_with_template_failure(self, mock_send):
        # Mock failed email sending
        mock_send.side_effect = Exception('SMTP error')
        
        # Send email
        result = EmailService.send_email_with_template(self.user, 'welcome')
        
        # Check result
        self.assertFalse(result)
        
        # Check that email log was created with failed status
        self.assertEqual(EmailLog.objects.count(), 1)
        email_log = EmailLog.objects.first()
        self.assertEqual(email_log.user, self.user)
        self.assertEqual(email_log.status, 'failed')
        self.assertIn('SMTP error', email_log.error_message)
        
    def test_send_email_with_nonexistent_template(self):
        # Send email with nonexistent template
        result = EmailService.send_email_with_template(self.user, 'nonexistent')
        
        # Check result
        self.assertFalse(result)
        
        # Check that email log was created with failed status
        self.assertEqual(EmailLog.objects.count(), 1)
        email_log = EmailLog.objects.first()
        self.assertEqual(email_log.user, self.user)
        self.assertEqual(email_log.status, 'failed')
        self.assertIn('does not exist', email_log.error_message)