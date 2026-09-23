from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from accounts.models import User, set_current_school
from schools.models import School, AcademicSession
from academics.models import Class, Section
from students.models import Student, ParentProfile
from fees.models import (
    FeeHead, FeeStructure, StudentFee, PaymentSubmission,
    FeePayment, FeeAdjustment, PaymentRefund, DailyFeeClosing, FeeAuditLog
)
from fees.forms import (
    PaymentClaimSubmissionForm, PaymentApprovalForm, PaymentRejectionForm,
    PaymentRefundForm, FeeAdjustmentForm, PaymentReversalForm
)
from fees.utils import generate_receipt_number, generate_claim_number, mask_student_name


class ProductionFeeSystemComprehensiveTest(TestCase):
    def setUp(self):
        # 1. School A
        self.school_a = School.objects.create(
            name="Greenwood International School",
            code="GREENWOOD",
            email="info@greenwood.com",
            phone="9876543210",
            address="123 Park Street"
        )
        self.session_a = AcademicSession.objects.create(
            school=self.school_a,
            name="2026-2027",
            start_date=date(2026, 4, 1),
            end_date=date(2027, 3, 31),
            is_current=True
        )
        self.class_a = Class.objects.create(school=self.school_a, name="Class 10", numeric_value=10)
        self.section_a = Section.objects.create(school=self.school_a, class_level=self.class_a, name="A")

        # School A Staff Users
        self.admin_a = User.objects.create_user(
            username="admin_a", password="password123", school=self.school_a, role=User.Roles.SCHOOL_ADMIN
        )
        self.principal_a = User.objects.create_user(
            username="principal_a", password="password123", school=self.school_a, role=User.Roles.PRINCIPAL
        )
        self.accountant_a = User.objects.create_user(
            username="accountant_a", password="password123", school=self.school_a, role=User.Roles.ACCOUNTANT
        )
        self.teacher_a = User.objects.create_user(
            username="teacher_a", password="password123", school=self.school_a, role=User.Roles.TEACHER
        )

        # School A Students & Parents
        self.student_user_1 = User.objects.create_user(
            username="student_rahul", password="password123", school=self.school_a, role=User.Roles.STUDENT
        )
        set_current_school(self.school_a)
        self.student_1 = Student.objects.create(
            school=self.school_a,
            user=self.student_user_1,
            admission_no="ADM-2026-001",
            roll_no="101",
            first_name="Rahul",
            last_name="Kumar",
            dob=date(2010, 5, 15),
            gender="M",
            admission_date=date(2026, 4, 1),
            academic_session=self.session_a,
            current_class=self.class_a,
            current_section=self.section_a,
            parent_phone="9876500001"
        )

        self.student_user_2 = User.objects.create_user(
            username="student_sneha", password="password123", school=self.school_a, role=User.Roles.STUDENT
        )
        self.student_2 = Student.objects.create(
            school=self.school_a,
            user=self.student_user_2,
            admission_no="ADM-2026-002",
            roll_no="102",
            first_name="Sneha",
            last_name="Patel",
            dob=date(2010, 8, 20),
            gender="F",
            admission_date=date(2026, 4, 1),
            academic_session=self.session_a,
            current_class=self.class_a,
            current_section=self.section_a,
            parent_phone="9876500002"
        )

        self.parent_user = User.objects.create_user(
            username="parent_ramesh", password="password123", school=self.school_a, role=User.Roles.PARENT
        )
        self.parent_profile = ParentProfile.objects.create(
            school=self.school_a,
            user=self.parent_user,
            father_name="Ramesh Kumar",
            primary_phone="9876500001"
        )
        self.parent_profile.students.add(self.student_1)

        # 2. School B (For Tenant Isolation Testing)
        self.school_b = School.objects.create(
            name="St. Xavier Academy",
            code="XAVIER",
            email="info@xavier.com",
            phone="1234567890"
        )
        self.admin_b = User.objects.create_user(
            username="admin_b", password="password123", school=self.school_b, role=User.Roles.SCHOOL_ADMIN
        )
        self.session_b = AcademicSession.objects.create(
            school=self.school_b,
            name="2026-2027",
            start_date=date(2026, 4, 1),
            end_date=date(2027, 3, 31),
            is_current=True
        )
        self.class_b = Class.objects.create(school=self.school_b, name="Class 10", numeric_value=10)
        self.sec_b = Section.objects.create(school=self.school_b, class_level=self.class_b, name="A")
        set_current_school(self.school_b)
        self.student_user_b = User.objects.create_user(
            username="student_bhavya", password="password123", school=self.school_b, role=User.Roles.STUDENT
        )
        self.student_b = Student.objects.create(
            school=self.school_b,
            user=self.student_user_b,
            admission_no="XAV-2026-001",
            first_name="Bhavya",
            last_name="Singh",
            dob=date(2010, 1, 1),
            academic_session=self.session_b,
            current_class=self.class_b,
            current_section=self.sec_b
        )

        # 3. Setup Fee Heads & Structures for School A
        set_current_school(self.school_a)
        self.fee_head_tuition = FeeHead.objects.create(school=self.school_a, name="Tuition Fee - September")
        self.fee_head_transport = FeeHead.objects.create(school=self.school_a, name="Transport Fee")
        self.fee_head_exam = FeeHead.objects.create(school=self.school_a, name="Exam Fee")

        self.fee_due_tuition = StudentFee.objects.create(
            school=self.school_a,
            academic_session=self.session_a,
            student=self.student_1,
            fee_head=self.fee_head_tuition,
            amount_due=Decimal("2500.00"),
            due_date=date(2026, 9, 30),
            status="PENDING"
        )
        self.fee_due_exam = StudentFee.objects.create(
            school=self.school_a,
            academic_session=self.session_a,
            student=self.student_1,
            fee_head=self.fee_head_exam,
            amount_due=Decimal("500.00"),
            due_date=date(2026, 9, 15),
            status="PENDING"
        )
        self.fee_due_student2 = StudentFee.objects.create(
            school=self.school_a,
            academic_session=self.session_a,
            student=self.student_2,
            fee_head=self.fee_head_tuition,
            amount_due=Decimal("2500.00"),
            due_date=date(2026, 9, 30),
            status="PENDING"
        )

        set_current_school(None)
        self.client = Client()

    # -------------------------------------------------------------
    # TEST 1: Golden Rule - Proof Submission NEVER auto-marks PAID
    # -------------------------------------------------------------
    def test_golden_rule_submission_does_not_mark_paid(self):
        self.client.login(username="student_rahul", password="password123")

        proof_file = SimpleUploadedFile("proof.jpg", b"fake_image_bytes", content_type="image/jpeg")
        post_data = {
            'amount': '2500.00',
            'payment_date': date.today().isoformat(),
            'payment_mode': 'UPI',
            'transaction_id': 'UPI98765432101',
            'bank_name': 'Google Pay',
            'proof_file': proof_file,
            'student_note': 'Paid tuition fee via GPay UTR 98765432101'
        }

        response = self.client.post(f"/fees/submit-claim/{self.fee_due_tuition.id}/", post_data)
        self.assertEqual(response.status_code, 302)

        self.fee_due_tuition.refresh_from_db()
        # Golden rule check: Fee status must NOT be PAID
        self.assertEqual(self.fee_due_tuition.amount_paid, Decimal("0.00"))
        self.assertNotEqual(self.fee_due_tuition.status, 'PAID')

        # Claim submission created with PENDING_VERIFICATION
        submission = PaymentSubmission.objects.filter(student_fee=self.fee_due_tuition).first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.status, 'PENDING_VERIFICATION')
        self.assertEqual(submission.amount, Decimal("2500.00"))
        self.assertEqual(submission.transaction_id, 'UPI98765432101')

        # Audit log verified
        audit_log = FeeAuditLog.objects.filter(action='PAYMENT_CLAIM_SUBMITTED').first()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.amount, Decimal("2500.00"))
        self.assertEqual(audit_log.student, self.student_1)

    # -------------------------------------------------------------
    # TEST 2: Overpayment & Negative Amount Prevention
    # -------------------------------------------------------------
    def test_overpayment_and_negative_amount_rejected(self):
        # 1. Overpayment: Due is ₹2,500, student attempts ₹5,000
        form_over = PaymentClaimSubmissionForm(
            data={
                'amount': '5000.00',
                'payment_date': date.today().isoformat(),
                'payment_mode': 'UPI',
                'transaction_id': 'TXN111111',
            },
            student_fee=self.fee_due_tuition,
            school=self.school_a
        )
        self.assertFalse(form_over.is_valid())
        self.assertIn('amount', form_over.errors)

        # 2. Negative amount
        form_neg = PaymentClaimSubmissionForm(
            data={
                'amount': '-100.00',
                'payment_date': date.today().isoformat(),
                'payment_mode': 'UPI',
                'transaction_id': 'TXN222222',
            },
            student_fee=self.fee_due_tuition,
            school=self.school_a
        )
        self.assertFalse(form_neg.is_valid())
        self.assertIn('amount', form_neg.errors)

    # -------------------------------------------------------------
    # TEST 3: Duplicate Transaction ID Prevention
    # -------------------------------------------------------------
    def test_duplicate_transaction_reference_prevention(self):
        # Create an existing verified submission with UTR12345
        PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-2026-000001",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="UTR12345",
            status="PENDING_VERIFICATION"
        )

        # Student attempts to submit the same UTR12345 again
        form = PaymentClaimSubmissionForm(
            data={
                'amount': '500.00',
                'payment_date': date.today().isoformat(),
                'payment_mode': 'UPI',
                'transaction_id': 'UTR12345',
            },
            student_fee=self.fee_due_exam,
            school=self.school_a
        )
        self.assertFalse(form.is_valid())
        self.assertIn('transaction_id', form.errors)

    # -------------------------------------------------------------
    # TEST 4: Multiple Pending Claims for Same Fee Due Prevention
    # -------------------------------------------------------------
    def test_multiple_active_pending_claims_prevented(self):
        PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-2026-000002",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="TXN-FIRST",
            status="PENDING_VERIFICATION"
        )

        self.client.login(username="student_rahul", password="password123")
        # Attempt to access submit claim view for the same fee due
        response = self.client.get(f"/fees/submit-claim/{self.fee_due_tuition.id}/")
        # Should redirect with warning
        self.assertEqual(response.status_code, 302)

    # -------------------------------------------------------------
    # TEST 5: Strict IDOR & Authorization Protection
    # -------------------------------------------------------------
    def test_idor_protection_student_cannot_access_other_student_data(self):
        self.client.login(username="student_rahul", password="password123")

        # Rahul attempts to submit payment claim for Sneha's fee due
        response = self.client.post(f"/fees/submit-claim/{self.fee_due_student2.id}/", {
            'amount': '2500.00',
            'payment_date': date.today().isoformat(),
            'payment_mode': 'UPI',
            'transaction_id': 'IDOR_TXN_001',
        })
        self.assertEqual(response.status_code, 403)

        # Create a payment and receipt for Sneha
        receipt_no_sneha = generate_receipt_number(self.school_a)
        payment_sneha = FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_student2,
            receipt_no=receipt_no_sneha,
            amount_paid=Decimal("2500.00"),
            payment_mode="UPI",
            status="VERIFIED"
        )

        # Rahul attempts to view/download Sneha's receipt
        response_rcpt = self.client.get(f"/fees/receipt/{payment_sneha.id}/")
        self.assertEqual(response_rcpt.status_code, 403)

        # Create a submission for Sneha
        submission_sneha = PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_student2,
            student=self.student_2,
            submission_no="CLM-SNEHA-001",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="SNEHA-TXN-1",
            status="PENDING_VERIFICATION"
        )

        # Rahul attempts to view Sneha's proof file
        response_proof = self.client.get(f"/fees/proof/{submission_sneha.id}/")
        self.assertEqual(response_proof.status_code, 403)

    # -------------------------------------------------------------
    # TEST 6: Parent Portal Access to Linked Children Only
    # -------------------------------------------------------------
    def test_parent_access_to_linked_children(self):
        self.client.login(username="parent_ramesh", password="password123")

        # Parent views My Fees (linked to Rahul)
        response = self.client.get("/fees/my-fees/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rahul")

        # Parent attempts to select unlinked student (Sneha)
        response_unlinked = self.client.get(f"/fees/my-fees/?student_id={self.student_2.id}")
        self.assertEqual(response_unlinked.status_code, 302)

    # -------------------------------------------------------------
    # TEST 7: Admin Verification & Atomic Ledger Update
    # -------------------------------------------------------------
    def test_admin_verification_workflow_atomic_success(self):
        claim = PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-2026-000100",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="AXIS-UPI-9999",
            status="PENDING_VERIFICATION"
        )

        self.client.login(username="accountant_a", password="password123")

        post_data = {
            'verified_amount': '2500.00',
            'payment_mode': 'UPI',
            'admin_notes': 'Verified in Axis Bank statement',
            'confirm_checkbox': 'on',
        }

        response = self.client.post(f"/fees/verifications/{claim.id}/approve/", post_data)
        self.assertEqual(response.status_code, 302)

        # Verify atomic state updates
        claim.refresh_from_db()
        self.assertEqual(claim.status, 'VERIFIED')
        self.assertEqual(claim.verified_by, self.accountant_a)

        self.fee_due_tuition.refresh_from_db()
        self.assertEqual(self.fee_due_tuition.amount_paid, Decimal("2500.00"))
        self.assertEqual(self.fee_due_tuition.status, 'PAID')
        self.assertEqual(self.fee_due_tuition.net_due, Decimal("0.00"))

        # Official FeePayment record created
        payment = FeePayment.objects.filter(submission=claim).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'VERIFIED')
        self.assertTrue(payment.receipt_no.startswith("REC-2026-"))
        self.assertEqual(payment.amount_paid, Decimal("2500.00"))

        # Immutable Audit Log created
        audit = FeeAuditLog.objects.filter(action='PAYMENT_APPROVED', payment=payment).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.user, self.accountant_a)
        self.assertEqual(audit.amount, Decimal("2500.00"))

    # -------------------------------------------------------------
    # TEST 8: Concurrency & Idempotency in Verification
    # -------------------------------------------------------------
    def test_concurrency_double_approval_prevention(self):
        claim = PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-CONCURRENT-01",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="CONC-TXN-01",
            status="PENDING_VERIFICATION"
        )

        self.client.login(username="admin_a", password="password123")

        # First approval
        res1 = self.client.post(f"/fees/verifications/{claim.id}/approve/", {
            'verified_amount': '2500.00',
            'payment_mode': 'UPI',
            'confirm_checkbox': 'on',
        })
        self.assertEqual(res1.status_code, 302)

        # Second concurrent approval attempt on same claim
        res2 = self.client.post(f"/fees/verifications/{claim.id}/approve/", {
            'verified_amount': '2500.00',
            'payment_mode': 'UPI',
            'confirm_checkbox': 'on',
        })
        # Should reject second approval without duplicate payment creation
        self.assertEqual(FeePayment.objects.filter(submission=claim).count(), 1)

    # -------------------------------------------------------------
    # TEST 9: Admin Rejection Workflow with Mandatory Reason
    # -------------------------------------------------------------
    def test_admin_rejection_workflow(self):
        claim = PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-REJECT-01",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="FAKE-UTR-000",
            status="PENDING_VERIFICATION"
        )

        self.client.login(username="admin_a", password="password123")

        # Attempt reject without reason -> should fail validation
        res_empty = self.client.post(f"/fees/verifications/{claim.id}/reject/", {'rejection_reason': ''})
        claim.refresh_from_db()
        self.assertEqual(claim.status, 'PENDING_VERIFICATION')

        # Reject with valid reason
        res_valid = self.client.post(f"/fees/verifications/{claim.id}/reject/", {
            'rejection_reason': 'UTR not found in school bank statement after 48 hours.'
        })
        self.assertEqual(res_valid.status_code, 302)

        claim.refresh_from_db()
        self.assertEqual(claim.status, 'REJECTED')
        self.assertEqual(claim.rejection_reason, 'UTR not found in school bank statement after 48 hours.')

        # Fee due remains pending
        self.fee_due_tuition.refresh_from_db()
        self.assertEqual(self.fee_due_tuition.status, 'PENDING')
        self.assertEqual(self.fee_due_tuition.amount_paid, Decimal("0.00"))

        # Audit log created
        audit = FeeAuditLog.objects.filter(action='PAYMENT_REJECTED', submission=claim).first()
        self.assertIsNotNone(audit)

    # -------------------------------------------------------------
    # TEST 10: Teacher Cannot Verify / Approve Payments (RBAC)
    # -------------------------------------------------------------
    def test_teacher_cannot_verify_payments(self):
        claim = PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-RBAC-01",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="RBAC-TXN-01",
            status="PENDING_VERIFICATION"
        )

        self.client.login(username="teacher_a", password="password123")

        # Teacher attempts to access verifications list
        res_list = self.client.get("/fees/verifications/")
        self.assertEqual(res_list.status_code, 302)

        # Teacher attempts to approve claim
        res_approve = self.client.post(f"/fees/verifications/{claim.id}/approve/", {
            'verified_amount': '2500.00',
            'payment_mode': 'UPI',
            'confirm_checkbox': 'on',
        })
        self.assertEqual(res_approve.status_code, 403)
        claim.refresh_from_db()
        self.assertEqual(claim.status, 'PENDING_VERIFICATION')

    # -------------------------------------------------------------
    # TEST 11: Public QR Receipt Verification & PII Protection
    # -------------------------------------------------------------
    def test_public_qr_receipt_verification_and_pii_masking(self):
        payment = FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            receipt_no="REC-2026-000145",
            amount_paid=Decimal("2500.00"),
            payment_mode="UPI",
            transaction_id="UPI-QR-TEST",
            status="VERIFIED"
        )

        # Anonymous / unauthenticated client scans QR token
        anon_client = Client()
        response = anon_client.get(f"/fees/receipt/verify/{payment.verification_token}/")
        self.assertEqual(response.status_code, 200)

        # Verify PII Masking: Should display "Rahul K." instead of full name or phone
        masked = mask_student_name(self.student_1)
        self.assertEqual(masked, "Rahul K.")
        self.assertContains(response, "Rahul K.")
        self.assertContains(response, "REC-2026-000145")
        self.assertContains(response, "Verified Authentic Receipt")

        # Test invalid token
        res_invalid = anon_client.get("/fees/receipt/verify/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(res_invalid.status_code, 404)
        self.assertContains(res_invalid, "Receipt Not Found or Invalid", status_code=404)

    # -------------------------------------------------------------
    # TEST 12: Fee Adjustments & Ledger Integrity
    # -------------------------------------------------------------
    def test_fee_adjustment_workflow(self):
        self.client.login(username="principal_a", password="password123")

        # Apply 10% concession (₹250) on ₹2,500 tuition fee
        response = self.client.post(f"/fees/adjustments/create/{self.fee_due_tuition.id}/", {
            'adjustment_type': 'DISCOUNT',
            'amount': '250.00',
            'reason': 'Merit Scholarship approved by Principal'
        })
        self.assertEqual(response.status_code, 302)

        self.fee_due_tuition.refresh_from_db()
        self.assertEqual(self.fee_due_tuition.amount_discount, Decimal("250.00"))
        self.assertEqual(self.fee_due_tuition.net_due, Decimal("2250.00"))

        # Verify audit log
        audit = FeeAuditLog.objects.filter(action='FEE_ADJUSTMENT').first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.amount, Decimal("250.00"))

    # -------------------------------------------------------------
    # TEST 13: Payment Void / Reversal Workflow
    # -------------------------------------------------------------
    def test_payment_void_reversal_workflow(self):
        payment = FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            receipt_no="REC-2026-000555",
            amount_paid=Decimal("2500.00"),
            payment_mode="CHEQUE",
            transaction_id="CHQ-987123",
            status="VERIFIED"
        )
        self.fee_due_tuition.refresh_from_db()
        self.assertEqual(self.fee_due_tuition.status, 'PAID')

        self.client.login(username="admin_a", password="password123")

        # Void / Reverse payment due to cheque bounce
        response = self.client.post(f"/fees/payment/{payment.id}/reverse/", {
            'reversal_reason': 'Cheque CHQ-987123 returned unpaid / bounced from bank.'
        })
        self.assertEqual(response.status_code, 302)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'REVERSED')
        self.assertEqual(payment.reversed_by, self.admin_a)

        # Ledger balance must be restored
        self.fee_due_tuition.refresh_from_db()
        self.assertEqual(self.fee_due_tuition.amount_paid, Decimal("0.00"))
        self.assertEqual(self.fee_due_tuition.net_due, Decimal("2500.00"))
        self.assertEqual(self.fee_due_tuition.status, 'PENDING')

        # Audit log check
        audit = FeeAuditLog.objects.filter(action='PAYMENT_REVERSED', payment=payment).first()
        self.assertIsNotNone(audit)

    # -------------------------------------------------------------
    # TEST 14: Fee Refund Request & Settlement
    # -------------------------------------------------------------
    def test_refund_workflow(self):
        payment = FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            receipt_no="REC-2026-000777",
            amount_paid=Decimal("2500.00"),
            payment_mode="BANK_TRANSFER",
            status="VERIFIED"
        )

        self.client.login(username="accountant_a", password="password123")

        # 1. Request Refund
        res_req = self.client.post(f"/fees/refunds/create/{payment.id}/", {
            'amount': '2500.00',
            'refund_mode': 'BANK_TRANSFER',
            'reason': 'Student transfer / withdrawal refund',
            'transaction_ref': 'REF-NEFT-9911'
        })
        self.assertEqual(res_req.status_code, 302)

        refund = PaymentRefund.objects.filter(payment=payment).first()
        self.assertIsNotNone(refund)
        self.assertEqual(refund.status, 'REQUESTED')

        # 2. Admin processes refund
        self.client.login(username="admin_a", password="password123")
        res_proc = self.client.post(f"/fees/refunds/{refund.id}/process/", {
            'action': 'APPROVE_PROCESS',
            'transaction_ref': 'BANK-TXN-REF-SUCCESS'
        })
        self.assertEqual(res_proc.status_code, 302)

        refund.refresh_from_db()
        self.assertEqual(refund.status, 'PROCESSED')

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'REFUNDED')

        self.fee_due_tuition.refresh_from_db()
        self.assertEqual(self.fee_due_tuition.amount_paid, Decimal("0.00"))

    # -------------------------------------------------------------
    # -------------------------------------------------------------
    # TEST 15: Immutability of FeeAuditLog (Security & Forensic Check)
    # -------------------------------------------------------------
    def test_fee_audit_log_immutability(self):
        log = FeeAuditLog.objects.create(
            school=self.school_a,
            user=self.admin_a,
            action='TEST_AUDIT_ACTION',
            amount=Decimal("1000.00"),
            details={'test_key': 'test_val'}
        )

        # 1. Direct instance modification blocked
        log.action = 'MODIFIED_ACTION'
        with self.assertRaises(PermissionDenied):
            log.save()

        # 2. Direct instance deletion blocked
        with self.assertRaises(PermissionDenied):
            log.delete()

        # 3. QuerySet bulk deletion blocked
        with self.assertRaises(PermissionDenied):
            FeeAuditLog.objects.filter(pk=log.pk).delete()

        # 4. QuerySet bulk update blocked
        with self.assertRaises(PermissionDenied):
            FeeAuditLog.objects.filter(pk=log.pk).update(action='HACKED')

    # -------------------------------------------------------------
    # TEST 16: Daily Fee Closing & Reconciliation
    # -------------------------------------------------------------
    def test_daily_closing_and_reconciliation(self):
        # Create cash and upi payments
        FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            receipt_no="REC-2026-900001",
            amount_paid=Decimal("2000.00"),
            payment_mode="CASH",
            payment_date=timezone.now(),
            status="VERIFIED"
        )
        FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_exam,
            receipt_no="REC-2026-900002",
            amount_paid=Decimal("500.00"),
            payment_mode="UPI",
            payment_date=timezone.now(),
            status="VERIFIED"
        )

        self.client.login(username="accountant_a", password="password123")

        today_str = date.today().isoformat()
        res_closing = self.client.post(f"/fees/daily-closing/?date={today_str}", {
            'notes': 'All cash verified in register.'
        })
        self.assertEqual(res_closing.status_code, 302)

        closing = DailyFeeClosing.objects.filter(school=self.school_a, closing_date=date.today()).first()
        self.assertIsNotNone(closing)
        self.assertEqual(closing.cash_total, Decimal("2000.00"))
        self.assertEqual(closing.upi_total, Decimal("500.00"))
        self.assertEqual(closing.total_collected, Decimal("2500.00"))

        # Reconciliation Report
        res_recon = self.client.get("/fees/reconciliation/")
        self.assertEqual(res_recon.status_code, 200)
        self.assertContains(res_recon, "Tuition Fee - September")

    # -------------------------------------------------------------
    # TEST 17: Multi-Tenant Isolation
    # -------------------------------------------------------------
    def test_multi_tenant_isolation(self):
        # School B Admin attempts to access School A's fee claims
        claim_a = PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-TENANT-A",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="TXN-A-01",
            status="PENDING_VERIFICATION"
        )

        self.client.login(username="admin_b", password="password123")

        # Admin B tries to approve School A's claim
        response = self.client.post(f"/fees/verifications/{claim_a.id}/approve/", {
            'verified_amount': '2500.00',
            'payment_mode': 'UPI',
            'confirm_checkbox': 'on',
        })
        # Should return 404 (because claim_a does not belong to school_b)
        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------------------
    # TEST 18: Permanent FeePayment Records (No Hard Delete)
    # -------------------------------------------------------------
    def test_fee_payment_no_hard_delete_protection(self):
        payment = FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            receipt_no="REC-2026-NODEL-001",
            amount_paid=Decimal("1500.00"),
            payment_mode="CASH",
            status="VERIFIED"
        )

        # Instance delete must raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            payment.delete()

        # Bulk queryset delete must raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            FeePayment.objects.filter(pk=payment.pk).delete()

    # -------------------------------------------------------------
    # TEST 19: Malformed UUID Public QR Verification (No 500 Crash)
    # -------------------------------------------------------------
    def test_malformed_and_invalid_uuid_receipt_verify(self):
        anon_client = Client()

        # Non-UUID string token -> 404 gracefully
        res_malformed = anon_client.get("/fees/receipt/verify/invalid-non-uuid-token/")
        self.assertEqual(res_malformed.status_code, 404)
        self.assertContains(res_malformed, "Receipt Not Found or Invalid", status_code=404)

        # Valid UUID format but non-existent token -> 404 gracefully
        res_nonexistent = anon_client.get("/fees/receipt/verify/11111111-2222-3333-4444-555555555555/")
        self.assertEqual(res_nonexistent.status_code, 404)
        self.assertContains(res_nonexistent, "Receipt Not Found or Invalid", status_code=404)

    # -------------------------------------------------------------
    # TEST 20: Cumulative Refund Limit Protection
    # -------------------------------------------------------------
    def test_cumulative_refund_limit_validation(self):
        payment = FeePayment.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            receipt_no="REC-2026-CUMUL-001",
            amount_paid=Decimal("2000.00"),
            payment_mode="UPI",
            status="VERIFIED"
        )

        # First partial refund of ₹1,200
        PaymentRefund.objects.create(
            school=self.school_a,
            payment=payment,
            refund_no="REF-2026-000001",
            amount=Decimal("1200.00"),
            reason="Partial scholarship credit",
            status="PROCESSED"
        )

        # Second refund form attempting ₹1,000 (1200 + 1000 = 2200 > 2000)
        form = PaymentRefundForm(
            data={
                'amount': '1000.00',
                'refund_mode': 'BANK_TRANSFER',
                'reason': 'Excess refund attempt'
            },
            payment=payment
        )
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

        # Valid refund of ₹800 (remaining balance)
        form_valid = PaymentRefundForm(
            data={
                'amount': '800.00',
                'refund_mode': 'BANK_TRANSFER',
                'reason': 'Final remaining balance refund'
            },
            payment=payment
        )
        self.assertTrue(form_valid.is_valid())

    # -------------------------------------------------------------
    # TEST 21: Student IDOR Protection on Directory & Student Profile
    # -------------------------------------------------------------
    def test_student_cannot_browse_directory_or_other_profiles(self):
        self.client.login(username="student_rahul", password="password123")

        # Student cannot browse school student list
        res_dir = self.client.get("/students/")
        self.assertEqual(res_dir.status_code, 302)

        # Student cannot view Sneha's student profile
        res_profile = self.client.get(f"/students/{self.student_2.id}/")
        self.assertEqual(res_profile.status_code, 302)

        # Student CAN view their own profile
        res_own_profile = self.client.get(f"/students/{self.student_1.id}/")
        self.assertEqual(res_own_profile.status_code, 200)

    # -------------------------------------------------------------
    # TEST 22: School Admin Dashboard Pending Verifications Banner
    # -------------------------------------------------------------
    def test_school_admin_dashboard_pending_verification_badge(self):
        # Create a pending payment claim
        PaymentSubmission.objects.create(
            school=self.school_a,
            student_fee=self.fee_due_tuition,
            student=self.student_1,
            submission_no="CLM-DASH-001",
            amount=Decimal("2500.00"),
            payment_date=date.today(),
            payment_mode="UPI",
            transaction_id="DASH-TXN-1",
            status="PENDING_VERIFICATION"
        )

        self.client.login(username="admin_a", password="password123")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment Claim Pending Verification")
        self.assertContains(response, "/fees/verifications/")
