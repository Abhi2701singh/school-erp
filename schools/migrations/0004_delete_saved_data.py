# Generated migration to delete all school, school admin, student, teacher records and retain superadmin

from django.db import migrations

def delete_all_school_data(apps, schema_editor):
    School = apps.get_model('schools', 'School')
    User = apps.get_model('accounts', 'User')

    # Delete all schools (which cascades to classes, sections, subjects, students, teachers, etc.)
    School.objects.all().delete()

    # Delete any non-superadmin users
    User.objects.filter(is_superuser=False).delete()
    User.objects.exclude(username='admin').delete()

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
        migrations.RunPython(delete_all_school_data, noop),
    ]
