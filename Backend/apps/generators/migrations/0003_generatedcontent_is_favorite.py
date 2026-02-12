# Migration to add is_favorite field - safe version that checks if column exists
# This migration handles the case where Django auto-generated a migration
# but the column already exists in the database
from django.db import migrations, models
from django.db import connection


def check_and_add_is_favorite(apps, schema_editor):
    """Check if is_favorite column exists, add it if it doesn't"""
    db_table = 'generated_contents'
    column_name = 'is_favorite'
    
    # Get the model to work with
    GeneratedContent = apps.get_model('generators', 'GeneratedContent')
    
    # Check if column exists in the database
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name=%s
            """, [db_table, column_name])
            column_exists = cursor.fetchone() is not None
        elif connection.vendor == 'sqlite':
            cursor.execute(f"PRAGMA table_info({db_table})")
            columns = [row[1] for row in cursor.fetchall()]
            column_exists = column_name in columns
        else:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name=%s
            """, [db_table, column_name])
            column_exists = cursor.fetchone() is not None
    
    # If column doesn't exist, add it using schema_editor
    if not column_exists:
        field = models.BooleanField(default=False, help_text='Whether this content is marked as favorite')
        field.set_attributes_from_name('is_favorite')
        schema_editor.add_field(GeneratedContent, field)


def reverse_add_is_favorite(apps, schema_editor):
    """Remove is_favorite column if it exists"""
    db_table = 'generated_contents'
    column_name = 'is_favorite'
    
    # Get the model to work with
    GeneratedContent = apps.get_model('generators', 'GeneratedContent')
    
    # Check if column exists in the database
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name=%s
            """, [db_table, column_name])
            column_exists = cursor.fetchone() is not None
        elif connection.vendor == 'sqlite':
            cursor.execute(f"PRAGMA table_info({db_table})")
            columns = [row[1] for row in cursor.fetchall()]
            column_exists = column_name in columns
        else:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name=%s
            """, [db_table, column_name])
            column_exists = cursor.fetchone() is not None
    
    # If column exists, remove it using schema_editor
    if column_exists:
        field = models.BooleanField(default=False)
        field.set_attributes_from_name('is_favorite')
        schema_editor.remove_field(GeneratedContent, field)


class Migration(migrations.Migration):

    dependencies = [
        ('generators', '0002_add_is_favorite'),
    ]

    operations = [
        migrations.RunPython(check_and_add_is_favorite, reverse_add_is_favorite),
    ]
