# Generated migration for initial GeneratedContent model
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('lesson_starter', 'Lesson Starter'), ('learning_objectives', 'Learning Objectives'), ('bell_ringer', 'Bell Ringer'), ('quiz', 'Quiz'), ('other', 'Other')], max_length=50)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('input_parameters', models.JSONField(blank=True, default=dict)),
                ('tokens_used', models.IntegerField(default=0)),
                ('generation_time', models.FloatField(blank=True, help_text='Generation time in seconds', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generated_content', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'generated content',
                'verbose_name_plural': 'generated contents',
                'db_table': 'generated_contents',
                'ordering': ['-created_at'],
            },
        ),
    ]

