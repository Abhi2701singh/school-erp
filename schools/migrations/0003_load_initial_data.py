# Migration kept for history, data loading disabled

from django.db import migrations

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0002_alter_school_address_alter_school_affiliation_no_and_more'),
        ('accounts', '0001_initial'),
        ('academics', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(noop, noop),
    ]

