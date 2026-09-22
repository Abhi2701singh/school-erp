# Generated migration to ensure all school notices are active

from django.db import migrations

def activate_all_notices(apps, schema_editor):
    Notice = apps.get_model('schools', 'Notice')
    Notice.objects.all().update(is_active=True)

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0004_delete_saved_data'),
    ]

    operations = [
        migrations.RunPython(activate_all_notices, noop),
    ]
