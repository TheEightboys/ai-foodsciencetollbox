# Generated migration for initial schema
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('trial', '7-Day Trial'), ('starter', 'Starter'), ('pro', 'Pro')], max_length=50, unique=True)),
                ('display_name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('monthly_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('generation_limit', models.IntegerField(blank=True, help_text='null = unlimited generations', null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('display_order', models.IntegerField(default=0)),
                ('features', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'membership_tiers',
                'ordering': ['display_order'],
            },
        ),
        migrations.CreateModel(
            name='UserMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generations_used_this_month', models.IntegerField(default=0)),
                ('last_reset_date', models.DateField(auto_now_add=True)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100)),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('active', 'Active'), ('past_due', 'Past Due'), ('canceled', 'Canceled'), ('trialing', 'Trialing')], default='active', max_length=20)),
                ('current_period_start', models.DateField(blank=True, null=True)),
                ('current_period_end', models.DateField(blank=True, null=True)),
                ('admin_override_unlimited', models.BooleanField(default=False)),
                ('admin_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tier', models.ForeignKey(on_delete=models.PROTECT, related_name='memberships', to='memberships.membershiptier')),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='membership', to='accounts.user')),
            ],
            options={
                'db_table': 'user_memberships',
            },
        ),
    ]

