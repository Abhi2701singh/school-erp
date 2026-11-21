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


from django.urls import reverse
from rest_framework.test import APIClient

class InactiveSchoolLockdownTest(TestCase):
    def setUp(self):
        self.superadmin = User.objects.create_superuser(
            username="superadmin", email="super@test.com", password="Password@123", role=User.Roles.SUPER_ADMIN
        )
        self.school = School.objects.create(name="Delhi Public School", code="DPS01", is_active=False)
        self.principal = User.objects.create_user(
            username="principal_dps", email="p@dps.com", password="Password@123",
            role=User.Roles.PRINCIPAL, school=self.school
        )
        self.teacher = User.objects.create_user(
            username="teacher_dps", email="t@dps.com", password="Password@123",
            role=User.Roles.TEACHER, school=self.school
        )
        self.api_client = APIClient()

    def test_inactive_school_web_login_blocked(self):
        # Inactive school principal tries to login
        res = self.client.post(reverse('login'), {'username': 'principal_dps', 'password': 'Password@123'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Access Disabled")
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_inactive_school_api_login_blocked(self):
        # Inactive school teacher tries to login via API
        res = self.api_client.post('/api/auth/login/', {'username': 'teacher_dps', 'password': 'Password@123'})
        self.assertEqual(res.status_code, 403)
        self.assertIn("deactivated", res.data.get('error', '').lower())

    def test_middleware_intercepts_existing_session_of_inactive_school(self):
        # Force login principal
        self.client.force_login(self.principal)
        # Access dashboard
        res = self.client.get(reverse('dashboard'))
        # Should be logged out and redirected to login
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('login'), res.url)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_student_admission_blocked_when_school_inactive(self):
        # Super admin enters portal of inactive school
        self.client.force_login(self.superadmin)
        session = self.client.session
        session['active_school_id'] = self.school.id
        session.save()

        # Try to admit student
        res = self.client.get(reverse('student_admission'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('student_list'), res.url)

    def test_notice_publishing_blocked_when_school_inactive(self):
        self.client.force_login(self.superadmin)
        session = self.client.session
        session['active_school_id'] = self.school.id
        session.save()

        res = self.client.post(reverse('notice_list'), {
            'title': 'Test Notice',
            'target_role': 'ALL',
            'content': 'This should be blocked.'
        })
        self.assertEqual(res.status_code, 302)
        from schools.models import Notice
        self.assertEqual(Notice.objects.filter(school=self.school).count(), 0)

    def test_toggle_school_status(self):
        self.client.force_login(self.superadmin)
        # School is currently inactive
        self.assertFalse(self.school.is_active)

        # Toggle to active
        res = self.client.get(reverse('school_toggle_status', kwargs={'pk': self.school.pk}))
        self.assertEqual(res.status_code, 302)
        self.school.refresh_from_db()
        self.assertTrue(self.school.is_active)

        # Now principal can log in
        res = self.client.post(reverse('login'), {'username': 'principal_dps', 'password': 'Password@123'})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('dashboard'))

