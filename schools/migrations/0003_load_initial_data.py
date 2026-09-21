# Generated manually to ensure zero data loss across deployments

from django.db import migrations
import datetime

def seed_initial_records(apps, schema_editor):
    School = apps.get_model('schools', 'School')
    AcademicSession = apps.get_model('schools', 'AcademicSession')
    User = apps.get_model('accounts', 'User')
    Class = apps.get_model('academics', 'Class')
    Section = apps.get_model('academics', 'Section')
    Subject = apps.get_model('academics', 'Subject')
    Student = apps.get_model('students', 'Student')

    # 1. School: ANGLE PUBLIC SCHOOL
    school, created = School.objects.get_or_create(
        code='211010',
        defaults={
            'name': 'ANGLE PUBLIC SCHOOL',
            'logo': 'school_logos/images_4pGBeIZ.jpeg',
            'address': 'xyz , 132 ewe , delhi',
            'phone': '9876543210',
            'email': 'angle@gmail.com',
            'principal_name': 'Abhinav Singh',
            'affiliation_no': 'cbse',
            'established_year': 2002,
            'is_active': True,
        }
    )

    # 2. Academic Session
    session, _ = AcademicSession.objects.get_or_create(
        school=school,
        name='2025-2026',
        defaults={
            'start_date': datetime.date(2025, 4, 1),
            'end_date': datetime.date(2026, 3, 31),
            'is_current': True
        }
    )

    # 3. Superadmin User
    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            first_name='Super',
            last_name='Admin',
            email='superadmin@test.com',
            role='SUPER_ADMIN',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            password='pbkdf2_sha256/xwkA7m2YNsK+zJPPPzMovhAi1A2o=' # admin123
        )

    # 4. School Admin User: angle
    if not User.objects.filter(username='angle').exists():
        User.objects.create(
            username='angle',
            first_name='ANGLE PUBLIC SCHOOL',
            last_name='Admin',
            email='angle@gmail.com',
            role='SCHOOL_ADMIN',
            school=school,
            is_staff=False,
            is_superuser=False,
            is_active=True,
            password='pbkdf2_sha256=' # Password@123
        )

    # 5. School Admin User: aps_admin
    if not User.objects.filter(username='aps_admin').exists():
        User.objects.create(
            username='aps_admin',
            first_name='APS',
            last_name='Admin',
            email='aps_admin@angle.edu',
            role='SCHOOL_ADMIN',
            school=school,
            is_staff=False,
            is_superuser=False,
            is_active=True,
            password='pbkdf2_sha256=' # Password@123
        )

    # 6. Student User: aman
    student_user = User.objects.filter(username='aman').first()
    if not student_user:
        student_user = User.objects.create(
            username='aman',
            first_name='Aman',
            last_name='Singh',
            email='xyz@gmail.com',
            role='STUDENT',
            school=school,
            is_staff=False,
            is_superuser=False,
            is_active=True,
            password='pbkdf2_sha256/Q2TEUHXB5ozQLI3X4dwGNc/wgBs=' # 01-01-2015
        )

    # 7. Classes: Nursery, LKG, UKG
    c_nursery, _ = Class.objects.get_or_create(school=school, name='Nursery', defaults={'numeric_value': 1})
    c_lkg, _ = Class.objects.get_or_create(school=school, name='LKG', defaults={'numeric_value': 2})
    c_ukg, _ = Class.objects.get_or_create(school=school, name='UKG', defaults={'numeric_value': 3})

    # 8. Sections
    sec_nursery, _ = Section.objects.get_or_create(school=school, class_level=c_nursery, name='A', defaults={'stream': 'General'})
    Section.objects.get_or_create(school=school, class_level=c_lkg, name='A', defaults={'stream': 'General'})
    Section.objects.get_or_create(school=school, class_level=c_ukg, name='A', defaults={'stream': 'General'})

    # 9. Subjects
    Subject.objects.get_or_create(school=school, code='math101', defaults={'name': 'math', 'subject_type': 'THEORY', 'max_marks': 100, 'pass_marks': 33})
    Subject.objects.get_or_create(school=school, code='eng102', defaults={'name': 'english', 'subject_type': 'THEORY', 'max_marks': 100, 'pass_marks': 33})
    Subject.objects.get_or_create(school=school, code='hindi103', defaults={'name': 'hindi', 'subject_type': 'THEORY', 'max_marks': 100, 'pass_marks': 33})

    # 10. Student: Aman Singh
    if not Student.objects.filter(school=school, admission_no='nus101').exists():
        Student.objects.create(
            school=school,
            user=student_user,
            admission_no='nus101',
            roll_no='101',
            first_name='Aman',
            last_name='Singh',
            dob=datetime.date(2015, 1, 1),
            gender='M',
            blood_group='o+',
            photo='student_photos/abhinav_pic-removebg-preview.jpg',
            govt_id='1234 3456 5678',
            address='ab , 180/18 , delhi',
            admission_date=datetime.date(2026, 8, 29),
            academic_session=session,
            current_class=c_nursery,
            current_section=sec_nursery,
            father_name='xyz singh',
            mother_name='qwe singh',
            guardian_name='xyz singh',
            parent_phone='1234567890',
            parent_email='xyz@gmail.com',
            parent_occupation='engg.',
            status='ACTIVE'
        )

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
        migrations.RunPython(seed_initial_records, noop),
    ]
