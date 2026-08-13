import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_erp.settings')
django.setup()

from accounts.models import User, set_current_school
from schools.models import School, AcademicSession, Notice
from academics.models import Class, Section, Subject, Timetable
from students.models import Student
from teachers.models import Teacher
from attendance.models import StudentAttendance
from examinations.models import Exam, MarksEntry
from fees.models import FeeHead, FeeStructure, StudentFee, FeePayment
from homework.models import Homework, StudyMaterial

def seed():
    print("Seeding Multi-School ERP Demo Data...")

    # 1. Super Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@edumanage.com', 'admin123', role=User.Roles.SUPER_ADMIN)
        print("Super Admin created: admin / admin123")

    # 2. School A: Greenwood High School
    school_a, created = School.objects.get_or_create(
        code="GREENWOOD",
        defaults={
            'name': "Greenwood High School",
            'address': "12 Park Street, Connaught Place, New Delhi",
            'phone': "+91 9876543210",
            'email': "info@greenwood.edu",
            'website': "https://greenwood.edu",
            'principal_name': "Dr. R. K. Sharma",
            'affiliation_no': "CBSE/AFF/2026/102",
            'established_year': 1998,
            'is_active': True
        }
    )

    # 3. School B: St. Xavier International School
    school_b, created = School.objects.get_or_create(
        code="XAVIER",
        defaults={
            'name': "St. Xavier International School",
            'address': "45 MG Road, Civil Lines, Mumbai",
            'phone': "+91 9811223344",
            'email': "contact@stxavier.edu",
            'website': "https://stxavier.edu",
            'principal_name': "Sister Mary Joseph",
            'affiliation_no': "ICSE/MUM/8821",
            'established_year': 2005,
            'is_active': True
        }
    )

    # 4. School Admins
    if not User.objects.filter(username='admin_greenwood').exists():
        User.objects.create_user('admin_greenwood', 'admin@greenwood.edu', 'Password@123', role=User.Roles.SCHOOL_ADMIN, school=school_a, first_name="Greenwood", last_name="Admin")
        print("Greenwood Admin created: admin_greenwood / Password@123")

    if not User.objects.filter(username='admin_xavier').exists():
        User.objects.create_user('admin_xavier', 'admin@stxavier.edu', 'Password@123', role=User.Roles.SCHOOL_ADMIN, school=school_b, first_name="Xavier", last_name="Admin")
        print("St. Xavier Admin created: admin_xavier / Password@123")

    # 5. Sessions
    session_a, _ = AcademicSession.objects.get_or_create(school=school_a, name="2025-2026", defaults={'start_date': date(2025, 4, 1), 'end_date': date(2026, 3, 31), 'is_current': True})
    session_b, _ = AcademicSession.objects.get_or_create(school=school_b, name="2025-2026", defaults={'start_date': date(2025, 4, 1), 'end_date': date(2026, 3, 31), 'is_current': True})

    # Set context to Greenwood High School for creating initial classes, subjects, students
    set_current_school(school_a)

    classes_list = ['Nursery', 'LKG', 'UKG', 'Class 1', 'Class 5', 'Class 10', 'Class 11', 'Class 12']
    classes_dict = {}
    for idx, cname in enumerate(classes_list, start=-2):
        cls, _ = Class.objects.get_or_create(school=school_a, name=cname, defaults={'numeric_value': idx})
        classes_dict[cname] = cls
        Section.objects.get_or_create(school=school_a, class_level=cls, name='A', defaults={'stream': 'General'})
        if cname in ['Class 11', 'Class 12']:
            Section.objects.get_or_create(school=school_a, class_level=cls, name='B', defaults={'stream': 'Science'})
            Section.objects.get_or_create(school=school_a, class_level=cls, name='C', defaults={'stream': 'Commerce'})

    # Subjects for Greenwood
    math, _ = Subject.objects.get_or_create(school=school_a, name="Mathematics", defaults={'code': 'MATH10', 'max_marks': 100, 'pass_marks': 33})
    phy, _ = Subject.objects.get_or_create(school=school_a, name="Physics", defaults={'code': 'PHY10', 'max_marks': 100, 'pass_marks': 33})
    eng, _ = Subject.objects.get_or_create(school=school_a, name="English Language", defaults={'code': 'ENG10', 'max_marks': 100, 'pass_marks': 33})

    cls_10 = classes_dict['Class 10']
    sec_10a = Section.objects.get(school=school_a, class_level=cls_10, name='A')

    # Teacher for Greenwood
    if not User.objects.filter(username='teacher_rahul').exists():
        t_user = User.objects.create_user('teacher_rahul', 'rahul@greenwood.edu', 'Teacher@123', role=User.Roles.TEACHER, school=school_a, first_name="Rahul", last_name="Verma")
        t_prof = Teacher.objects.create(school=school_a, user=t_user, employee_id="EMP2026-01", qualification="M.Sc. Mathematics", phone="+91 9876500112", joining_date=date(2022, 6, 1))
        t_prof.assigned_classes.add(cls_10)
        t_prof.assigned_sections.add(sec_10a)
        t_prof.assigned_subjects.add(math, phy)
        print("Teacher created: teacher_rahul / Teacher@123")

    # Students for Greenwood
    if not Student.objects.filter(school=school_a, admission_no="ADM2026-101").exists():
        st_user1 = User.objects.create_user('greenwood_adm2026-101', 'abhinav@parent.com', 'Password@123', role=User.Roles.STUDENT, school=school_a, first_name="Abhinav", last_name="Kumar")
        st1 = Student.objects.create(
            school=school_a,
            user=st_user1,
            admission_no="ADM2026-101",
            roll_no="101",
            first_name="Abhinav",
            last_name="Kumar",
            dob=date(2010, 8, 15),
            gender="M",
            blood_group="O+",
            address="A-45, Green Park, New Delhi",
            admission_date=date(2025, 4, 2),
            academic_session=session_a,
            current_class=cls_10,
            current_section=sec_10a,
            father_name="Rajesh Kumar",
            mother_name="Sunita Kumar",
            parent_phone="+91 9988776655",
            parent_email="rajesh.kumar@gmail.com",
            status="ACTIVE"
        )
        print("Student created: Abhinav Kumar (ADM2026-101)")

    if not Student.objects.filter(school=school_a, admission_no="ADM2026-102").exists():
        st_user2 = User.objects.create_user('greenwood_adm2026-102', 'priya@parent.com', 'Password@123', role=User.Roles.STUDENT, school=school_a, first_name="Priya", last_name="Sharma")
        st2 = Student.objects.create(
            school=school_a,
            user=st_user2,
            admission_no="ADM2026-102",
            roll_no="102",
            first_name="Priya",
            last_name="Sharma",
            dob=date(2010, 11, 20),
            gender="F",
            blood_group="A+",
            address="B-12, South Extension, New Delhi",
            admission_date=date(2025, 4, 5),
            academic_session=session_a,
            current_class=cls_10,
            current_section=sec_10a,
            father_name="Anil Sharma",
            mother_name="Meena Sharma",
            parent_phone="+91 9988776644",
            parent_email="anil.sharma@gmail.com",
            status="ACTIVE"
        )
        print("Student created: Priya Sharma (ADM2026-102)")

    # Fee Head & Structure for Greenwood
    fh_tuition, _ = FeeHead.objects.get_or_create(school=school_a, name="Tuition Fee")
    fh_adm, _ = FeeHead.objects.get_or_create(school=school_a, name="Admission Fee")

    fs1, _ = FeeStructure.objects.get_or_create(school=school_a, academic_session=session_a, class_level=cls_10, fee_head=fh_tuition, defaults={'amount': 4500.00, 'frequency': 'MONTHLY', 'due_date': date(2026, 8, 31)})
    fs2, _ = FeeStructure.objects.get_or_create(school=school_a, academic_session=session_a, class_level=cls_10, fee_head=fh_adm, defaults={'amount': 10000.00, 'frequency': 'ANNUAL', 'due_date': date(2025, 4, 30)})

    # Assign student fees
    st1 = Student.objects.get(school=school_a, admission_no="ADM2026-101")
    StudentFee.objects.get_or_create(school=school_a, academic_session=session_a, student=st1, fee_head=fh_tuition, due_date=date(2026, 8, 31), defaults={'amount_due': 4500.00})
    StudentFee.objects.get_or_create(school=school_a, academic_session=session_a, student=st1, fee_head=fh_adm, due_date=date(2025, 4, 30), defaults={'amount_due': 10000.00})

    # Sample Exam & Marks for Greenwood
    exam, _ = Exam.objects.get_or_create(school=school_a, academic_session=session_a, class_level=cls_10, name="Half Yearly Examination 2026", defaults={'exam_type': 'HALF_YEARLY', 'start_date': date(2026, 9, 15), 'end_date': date(2026, 9, 25), 'is_published': True})
    MarksEntry.objects.get_or_create(school=school_a, exam=exam, student=st1, subject=math, defaults={'theory_marks_obtained': 85.0, 'practical_marks_obtained': 0.0})
    MarksEntry.objects.get_or_create(school=school_a, exam=exam, student=st1, subject=phy, defaults={'theory_marks_obtained': 78.0, 'practical_marks_obtained': 15.0})

    # Notice for Greenwood
    Notice.objects.get_or_create(school=school_a, title="Independence Day Function Notice", defaults={'content': "Flag hoisting ceremony will be held at 8:00 AM in the school main ground.", 'target_role': 'ALL'})

    # Now set context to St. Xavier to prove isolation
    set_current_school(school_b)
    cls_x, _ = Class.objects.get_or_create(school=school_b, name="Class 10", defaults={'numeric_value': 10})
    sec_x, _ = Section.objects.get_or_create(school=school_b, class_level=cls_x, name='A', defaults={'stream': 'General'})
    st_x_user = User.objects.create_user('xavier_xav-2026-01', 'mumbai@parent.com', 'Password@123', role=User.Roles.STUDENT, school=school_b, first_name="Rohan", last_name="Deshmukh")
    Student.objects.get_or_create(
        school=school_b,
        admission_no="XAV-2026-01",
        defaults={
            'user': st_x_user,
            'roll_no': "01",
            'first_name': "Rohan",
            'last_name': "Deshmukh",
            'dob': date(2010, 5, 12),
            'gender': "M",
            'address': "Bandra, Mumbai",
            'admission_date': date(2025, 4, 1),
            'academic_session': session_b,
            'current_class': cls_x,
            'current_section': sec_x,
            'father_name': "Vijay Deshmukh",
            'parent_phone': "+91 9123456789",
            'status': "ACTIVE"
        }
    )

    print("Demo data seeded successfully across multiple schools!")

if __name__ == '__main__':
    seed()
