# Generated migration for initial accounts app schema
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='TeacherProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_academy_member', models.BooleanField(default=False, help_text='Food Science Academy member')),
                ('email_verified', models.BooleanField(default=False)),
                ('email_verification_token', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('email_verification_sent_at', models.DateTimeField(blank=True, null=True)),
                ('password_reset_token', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('password_reset_expires', models.DateTimeField(blank=True, null=True)),
                ('terms_accepted', models.BooleanField(default=False)),
                ('terms_accepted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='teacher_profile', to='accounts.User')),
            ],
            options={
                'verbose_name': 'teacher profile',
                'verbose_name_plural': 'teacher profiles',
                'db_table': 'teacher_profiles',
            },
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_grade_level', models.CharField(choices=[('middle_school', 'Middle School (6-8)'), ('high_school', 'High School (9-12)'), ('mixed', 'Mixed Grade Levels')], default='high_school', max_length=50)),
                ('preferred_subject', models.CharField(choices=[('food_science', 'Food Science'), ('consumer_science', 'Consumer Science'), ('nutrition', 'Nutrition'), ('culinary', 'Culinary Arts'), ('home_economics', 'Home Economics')], default='food_science', max_length=100)),
                ('preferred_tone', models.CharField(choices=[('formal', 'Formal & Academic'), ('conversational', 'Conversational & Friendly'), ('balanced', 'Balanced')], default='balanced', max_length=50)),
                ('default_question_count', models.IntegerField(default=5)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='preferences', to='accounts.User')),
            ],
            options={
                'verbose_name': 'user preferences',
                'verbose_name_plural': 'user preferences',
                'db_table': 'user_preferences',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]

