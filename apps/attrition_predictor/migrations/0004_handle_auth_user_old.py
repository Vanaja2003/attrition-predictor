from django.db import migrations

def forwards_func(apps, schema_editor):
    # Get the database connection
    connection = schema_editor.connection
    cursor = connection.cursor()
    
    # Check if the table exists and drop it if it does
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='auth_user__old';
    """)
    if cursor.fetchone():
        cursor.execute('DROP TABLE auth_user__old;')

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('attrition_predictor', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
