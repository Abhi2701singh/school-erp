import datetime
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from schools.models import School, AcademicSession
from academics.models import Class, Section, Subject, Timetable
from students.models import Student, ParentProfile

class TimetableComprehensiveTestCase(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Test Model School", code="TMS01")
        self.session = AcademicSession.objects.create(
            school=self.school, name="2026-2027",
            start_date=datetime.date(2026, 4, 1),
            end_date=datetime.date(2027, 3, 31),
            is_current=True
        )

        # Classes & Sections
        self.class10 = Class.objects.create(school=self.school, name="Class 10", numeric_value=10)
        self.sec10A = Section.objects.create(school=self.school, class_level=self.class10, name="A")

        self.class12 = Class.objects.create(school=self.school, name="Class 12", numeric_value=12)
        self.sec12A = Section.objects.create(school=self.school, class_level=self.class12, name="A")

        # Subjects
        self.maths = Subject.objects.create(school=self.school, name="Mathematics", code="MTH10")
        self.physics = Subject.objects.create(school=self.school, name="Physics", code="PHY12")

        # Users
        self.admin_user = User.objects.create_user(
            username="admin_tt", password="password123", role="SCHOOL_ADMIN", school=self.school
        )

        self.teacher_user = User.objects.create_user(
            username="teacher_tt", password="password123", role="TEACHER", school=self.school, first_name="Ramesh", last_name="Sharma"
        )

        self.student_user = User.objects.create_user(
            username="student_tt", password="password123", role="STUDENT", school=self.school
        )
        self.student = Student.objects.create(
            school=self.school,
            user=self.student_user,
            admission_no="ADM-1001",
            first_name="Rahul",
            last_name="Verma",
            dob=datetime.date(2010, 5, 15),
            academic_session=self.session,
            current_class=self.class10,
            current_section=self.sec10A
        )

        self.parent_user = User.objects.create_user(
            username="parent_tt", password="password123", role="PARENT", school=self.school
        )
        self.parent_prof = ParentProfile.objects.create(
            school=self.school, user=self.parent_user, primary_phone="9876543210"
        )
        self.parent_prof.students.add(self.student)

        # Timetable entries
        self.tt_p1 = Timetable.objects.create(
            school=self.school,
            class_level=self.class10,
            section=self.sec10A,
            subject=self.maths,
            teacher_user=self.teacher_user,
            day="Monday",
            period_number=1,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(9, 40)
        )

        self.tt_p5 = Timetable.objects.create(
            school=self.school,
            class_level=self.class10,
            section=self.sec10A,
            subject=self.maths,
            teacher_user=self.teacher_user,
            day="Monday",
            period_number=5,
            start_time=datetime.time(12, 20),
            end_time=datetime.time(13, 0)
        )

        self.tt_c12 = Timetable.objects.create(
            school=self.school,
            class_level=self.class12,
            section=self.sec12A,
            subject=self.physics,
            teacher_user=self.teacher_user,
            day="Monday",
            period_number=1,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(9, 40)
        )

        self.client = Client()

    def test_admin_can_view_and_filter_any_class_timetable(self):
        self.client.login(username="admin_tt", password="password123")
        res = self.client.get(reverse('timetable') + f"?class_id={self.class12.id}&section_id={self.sec12A.id}")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Physics")
        self.assertContains(res, "09:00 AM - 09:40 AM")
        self.assertContains(res, "BREAK")
        self.assertContains(res, "11:40 AM - 12:20 PM")

    def test_student_locked_to_own_class_and_ignores_tampering(self):
        self.client.login(username="student_tt", password="password123")
        # Try to maliciously view Class 12 timetable
        res = self.client.get(reverse('timetable') + f"?class_id={self.class12.id}&section_id={self.sec12A.id}")
        self.assertEqual(res.status_code, 200)
        # Should only see Class 10 subjects
        self.assertContains(res, "Mathematics")
        self.assertNotContains(res, "Physics")
        self.assertContains(res, "Class 10")
        self.assertContains(res, "09:00 AM - 09:40 AM")
        self.assertContains(res, "BREAK")

    def test_parent_access_timetable_no_server_error(self):
        self.client.login(username="parent_tt", password="password123")
        res = self.client.get(reverse('timetable'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Mathematics")
        self.assertContains(res, "11:40 AM - 12:20 PM")

    def test_principal_access_and_save_routine_settings(self):
        principal = User.objects.create_user(
            username="principal_tt", password="password123", role="PRINCIPAL", school=self.school
        )
        self.client.login(username="principal_tt", password="password123")
        res = self.client.get(reverse('timetable'))
        self.assertEqual(res.status_code, 200)

        # Save routine settings: 6 periods with break after period 3
        post_res = self.client.post(reverse('timetable') + f"?class_id={self.class10.id}&section_id={self.sec10A.id}", {
            'action': 'save_settings',
            'total_periods': 6,
            'break_after_period': 3,
            'break_start_time': '10:30',
            'break_end_time': '11:00',
            'has_break': '1',
            'apply_to_all': '1'
        })
        self.assertEqual(post_res.status_code, 302)

        # View updated timetable
        res_after = self.client.get(reverse('timetable') + f"?class_id={self.class10.id}&section_id={self.sec10A.id}")
        self.assertEqual(res_after.status_code, 200)
        self.assertContains(res_after, "10:30 AM - 11:00 AM")
        self.assertContains(res_after, "3rd")
        self.assertContains(res_after, "6th")

    def test_timetable_api_student_locked(self):
        from rest_framework.test import APIClient
        api_client = APIClient()
        api_client.force_authenticate(user=self.student_user)
        res = api_client.get(reverse('api_timetable') + f"?class_id={self.class12.id}&section_id={self.sec12A.id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['selected_class']['id'], self.class10.id)
        self.assertTrue(data['is_student'])
        self.assertIn('period_timings', data)
        self.assertIn('break_timing', data)

