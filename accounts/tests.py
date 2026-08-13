from django.test import TestCase
from datetime import date
from accounts.models import User, set_current_school
from schools.models import School, AcademicSession
from students.models import Student
from academics.models import Class, Section

class MultiTenantIsolationTest(TestCase):
    def setUp(self):
        # Create School A
        self.school_a = School.objects.create(name="Greenwood High", code="GREENWOOD", email="a@greenwood.com", phone="123")
        self.session_a = AcademicSession.objects.create(school=self.school_a, name="2025-26", start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True)
        self.cls_a = Class.objects.create(school=self.school_a, name="Class 10", numeric_value=10)
        self.sec_a = Section.objects.create(school=self.school_a, class_level=self.cls_a, name="A")

        # Create School B
        self.school_b = School.objects.create(name="St Xavier", code="XAVIER", email="b@xavier.com", phone="456")
        self.session_b = AcademicSession.objects.create(school=self.school_b, name="2025-26", start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True)
        self.cls_b = Class.objects.create(school=self.school_b, name="Class 10", numeric_value=10)
        self.sec_b = Section.objects.create(school=self.school_b, class_level=self.cls_b, name="A")

        # Create Student A under School A
        set_current_school(self.school_a)
        self.student_a = Student.objects.create(
            school=self.school_a, admission_no="ADM-A-01", first_name="Aarav", dob=date(2010, 1, 1),
            gender="M", admission_date=date(2025, 4, 1), academic_session=self.session_a,
            current_class=self.cls_a, current_section=self.sec_a, father_name="Ram", parent_phone="999"
        )

        # Create Student B under School B
        set_current_school(self.school_b)
        self.student_b = Student.objects.create(
            school=self.school_b, admission_no="ADM-B-01", first_name="Bhavya", dob=date(2010, 2, 2),
            gender="F", admission_date=date(2025, 4, 1), academic_session=self.session_b,
            current_class=self.cls_b, current_section=self.sec_b, father_name="Shyam", parent_phone="888"
        )

    def test_tenant_isolation(self):
        # 1. When Context is School A
        set_current_school(self.school_a)
        students_a = Student.objects.all()
        self.assertIn(self.student_a, students_a)
        self.assertNotIn(self.student_b, students_a)
        self.assertEqual(students_a.count(), 1)

        # 2. When Context is School B
        set_current_school(self.school_b)
        students_b = Student.objects.all()
        self.assertIn(self.student_b, students_b)
        self.assertNotIn(self.student_a, students_b)
        self.assertEqual(students_b.count(), 1)

        # 3. When Context is Super Admin (None)
        set_current_school(None)
        all_students = Student.objects.all()
        self.assertIn(self.student_a, all_students)
        self.assertIn(self.student_b, all_students)
        self.assertEqual(all_students.count(), 2)
