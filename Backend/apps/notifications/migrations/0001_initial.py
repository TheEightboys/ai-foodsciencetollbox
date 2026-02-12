# Generated manually for notifications app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('welcome', 'Welcome Email'), ('email_verification', 'Email Verification'), ('password_reset', 'Password Reset'), ('upgrade_confirmation', 'Upgrade Confirmation'), ('limit_reached', 'Generation Limit Reached'), ('limit_reached_trial', 'Generation Limit Reached - Trial'), ('limit_reached_starter', 'Generation Limit Reached - Starter'), ('90_percent_usage', '90% Usage Notification'), ('monthly_reset', 'Monthly Usage Reset'), ('support_acknowledgment', 'Support Ticket Acknowledgment')], max_length=50, unique=True)),
                ('subject', models.CharField(max_length=200)),
                ('plain_text_content', models.TextField()),
                ('html_content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'email template',
                'verbose_name_plural': 'email templates',
                'db_table': 'email_templates',
            },
        ),
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('recipient', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('failed', 'Failed')], default='sent', max_length=10)),
                ('plain_text_content', models.TextField()),
                ('html_content', models.TextField(blank=True)),
                ('error_message', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notifications.emailtemplate')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'email log',
                'verbose_name_plural': 'email logs',
                'db_table': 'email_logs',
                'ordering': ['-sent_at'],
            },
        ),
        migrations.CreateModel(
            name='FeatureNotificationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_name', models.CharField(max_length=200)),
                ('user_email', models.EmailField(max_length=254)),
                ('notified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notified_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feature_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'feature notification request',
                'verbose_name_plural': 'feature notification requests',
                'db_table': 'feature_notification_requests',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'feature_name')},
            },
        ),
    ]

