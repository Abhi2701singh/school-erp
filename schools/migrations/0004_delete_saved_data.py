# Migration history preserved, data deletion disabled

from django.db import migrations

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0003_load_initial_data'),
        ('accounts', '0001_initial'),
        ('students', '0001_initial'),
        ('teachers', '0001_initial'),
        ('academics', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(noop, noop),
    ]

