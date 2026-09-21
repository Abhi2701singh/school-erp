import datetime

def seed_default_records():
    try:
        from schools.models import School, AcademicSession
        from accounts.models import User
        from academics.models import Class, Section, Subject
        from students.models import Student

        # 1. School: ANGLE PUBLIC SCHOOL
        school, _ = School.objects.get_or_create(
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

        # 3. Superadmin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='superadmin@test.com',
                password='admin123',
                role=User.Roles.SUPER_ADMIN,
                first_name='Super',
                last_name='Admin'
            )

        # 4. School Admin User: angle
        admin_angle = User.objects.filter(username='angle').first()
        if not admin_angle:
            admin_angle = User.objects.create_user(
                username='angle',
                email='angle@gmail.com',
                password='Password@123',
                role=User.Roles.SCHOOL_ADMIN,
                school=school,
                first_name='ANGLE PUBLIC SCHOOL',
                last_name='Admin'
            )
        else:
            if admin_angle.school_id != school.id:
                admin_angle.school = school
                admin_angle.role = User.Roles.SCHOOL_ADMIN
                admin_angle.save()

        # 5. Student User: aman
        student_user = User.objects.filter(username='aman').first()
        if not student_user:
            student_user = User.objects.create_user(
                username='aman',
                email='xyz@gmail.com',
                password='01-01-2015',
                role=User.Roles.STUDENT,
                school=school,
                first_name='Aman',
                last_name='Singh'
            )
        else:
            if student_user.school_id != school.id:
                student_user.school = school
                student_user.role = User.Roles.STUDENT
                student_user.save()

        # 6. Classes & Sections
        c_nursery, _ = Class.objects.get_or_create(school=school, name='Nursery', defaults={'numeric_value': 1})
        c_lkg, _ = Class.objects.get_or_create(school=school, name='LKG', defaults={'numeric_value': 2})
        c_ukg, _ = Class.objects.get_or_create(school=school, name='UKG', defaults={'numeric_value': 3})

        sec_nursery, _ = Section.objects.get_or_create(school=school, class_level=c_nursery, name='A', defaults={'stream': 'General'})
        Section.objects.get_or_create(school=school, class_level=c_lkg, name='A', defaults={'stream': 'General'})
        Section.objects.get_or_create(school=school, class_level=c_ukg, name='A', defaults={'stream': 'General'})

        # 7. Subjects
        Subject.objects.get_or_create(school=school, code='math101', defaults={'name': 'math', 'subject_type': 'THEORY', 'max_marks': 100, 'pass_marks': 33})
        Subject.objects.get_or_create(school=school, code='eng102', defaults={'name': 'english', 'subject_type': 'THEORY', 'max_marks': 100, 'pass_marks': 33})
        Subject.objects.get_or_create(school=school, code='hindi103', defaults={'name': 'hindi', 'subject_type': 'THEORY', 'max_marks': 100, 'pass_marks': 33})

        # 8. Student Record: Aman Singh
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
    except Exception as e:
        print(f'[Seed warning]: {e}')
