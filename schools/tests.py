from django.test import TestCase, Client
from django.urls import reverse
from schools.models import School
from accounts.models import User


class SchoolPaymentGatewaySettingsTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Delhi Public School",
            code="DPS01",
            email="admin@dps01.edu",
            phone="9876543210",
            address="Sector 5, Rohini"
        )
        self.admin_user = User.objects.create_user(
            username="dps_admin",
            password="password123",
            role="PRINCIPAL",
            school=self.school
        )
        self.student_user = User.objects.create_user(
            username="dps_student",
            password="password123",
            role="STUDENT",
            school=self.school
        )
        self.client = Client()

    def test_payment_gateway_property(self):
        # By default not configured
        self.assertFalse(self.school.has_active_payment_gateway)

        # Set keys but payments disabled
        self.school.razorpay_key_id = "rzp_test_abc"
        self.school.razorpay_key_secret = "secret_123"
        self.school.online_payments_enabled = False
        self.school.save()
        self.assertFalse(self.school.has_active_payment_gateway)

        # Enable payments with valid keys
        self.school.online_payments_enabled = True
        self.school.save()
        self.assertTrue(self.school.has_active_payment_gateway)

    def test_payment_settings_view_permissions(self):
        url = reverse('school_gateway_settings')

        # 1. Anonymous user redirected to login
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)

        # 2. Student user redirected to dashboard with permission error
        self.client.login(username="dps_student", password="password123")
        res = self.client.get(url)
        self.assertRedirects(res, reverse('dashboard'))

        # 3. School admin / Principal allowed (200)
        self.client.login(username="dps_admin", password="password123")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Payment Gateway Setup")

    def test_payment_settings_update_keys_and_bank(self):
        self.client.login(username="dps_admin", password="password123")
        url = reverse('school_gateway_settings')

        payload = {
            'online_payments_enabled': 'on',
            'razorpay_key_id': 'rzp_test_NEW_KEY',
            'razorpay_key_secret': 'super_secret_456',
            'razorpay_webhook_secret': 'whsec_789',
            'upi_id': 'dps.fees@icici',
            'bank_name': 'ICICI Bank',
            'bank_account_no': '123456789012',
            'bank_ifsc': 'ICIC0001234',
        }
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, 302)

        self.school.refresh_from_db()
        self.assertTrue(self.school.online_payments_enabled)
        self.assertEqual(self.school.razorpay_key_id, 'rzp_test_NEW_KEY')
        self.assertEqual(self.school.razorpay_key_secret, 'super_secret_456')
        self.assertEqual(self.school.upi_id, 'dps.fees@icici')
        self.assertEqual(self.school.bank_name, 'ICICI Bank')
        self.assertEqual(self.school.bank_account_no, '123456789012')
        self.assertEqual(self.school.bank_ifsc, 'ICIC0001234')
        self.assertTrue(self.school.has_active_payment_gateway)
