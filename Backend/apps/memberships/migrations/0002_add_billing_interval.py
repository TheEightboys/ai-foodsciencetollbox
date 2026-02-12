# Generated migration for adding billing_interval field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermembership',
            name='billing_interval',
            field=models.CharField(blank=True, choices=[('month', 'Monthly'), ('year', 'Yearly')], help_text='Billing interval: monthly or yearly subscription', max_length=10, null=True),
        ),
    ]

