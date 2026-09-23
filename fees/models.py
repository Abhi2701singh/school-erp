import os
import uuid
from datetime import date
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from accounts.models import TenantModel, User, TenantManager, get_current_school
from schools.models import AcademicSession
from academics.models import Class
from students.models import Student


def secure_fee_proof_path(instance, filename):
    """
    Generate randomized secure path for student payment proofs.
    Never use original user-supplied filenames directly.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.pdf', '.webp']:
        ext = '.jpg'
    now = timezone.now()
    return f"fee_proofs/{now.year}/{now.month:02d}/{uuid.uuid4().hex}{ext}"


class FeeHead(TenantModel):
    name = models.CharField(max_length=100, help_text="e.g. Tuition Fee, Admission Fee, Exam Fee, Transport Fee")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.school.code if self.school_id else ''})"


class FeeStructure(TenantModel):
    FREQ_CHOICES = (
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUAL', 'Annual / One-Time'),
    )

    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="fee_structures")
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="fee_structures")
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQ_CHOICES, default='MONTHLY')
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['class_level', 'fee_head']

    def __str__(self):
        return f"{self.class_level.name} - {self.fee_head.name} : ₹{self.amount} ({self.get_frequency_display()})"


class StudentFee(TenantModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending / Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    )

    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="student_fees")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['due_date', 'student']

    @property
    def net_due(self):
        due = self.amount_due or Decimal('0.00')
        disc = self.amount_discount or Decimal('0.00')
        paid = self.amount_paid or Decimal('0.00')
        val = due - disc - paid
        return max(Decimal('0.00'), val)

    @property
    def is_overdue(self):
        return bool(self.due_date and date.today() > self.due_date and self.net_due > Decimal('0.00'))

    @property
    def previous_arrears(self):
        """
        Calculate total unpaid arrears/dues from previous fees for this student.
        Includes all earlier fee records for this student with due_date < this due_date.
        """
        if not self.student_id or not self.school_id:
            return Decimal('0.00')
        if self.due_date:
            past_fees = StudentFee.objects.filter(
                school=self.school,
                student=self.student,
                due_date__lt=self.due_date
            ).exclude(pk=self.pk)
        else:
            past_fees = StudentFee.objects.filter(
                school=self.school,
                student=self.student,
                pk__lt=self.pk if self.pk else 0
            ).exclude(pk=self.pk)
        return sum([f.net_due for f in past_fees], Decimal('0.00'))

    @property
    def total_payable_with_arrears(self):
        """Total payable including this fee's net due + past unpaid arrears."""
        return self.net_due + self.previous_arrears

    def get_past_unpaid_fee_items(self):
        """Return list of past unpaid fee objects for itemized display."""
        if not self.student_id or not self.school_id:
            return []
        if self.due_date:
            past_fees = StudentFee.objects.filter(
                school=self.school,
                student=self.student,
                due_date__lt=self.due_date
            ).exclude(pk=self.pk).select_related('fee_head', 'academic_session')
        else:
            past_fees = StudentFee.objects.filter(
                school=self.school,
                student=self.student,
                pk__lt=self.pk if self.pk else 0
            ).exclude(pk=self.pk).select_related('fee_head', 'academic_session')
        return [f for f in past_fees if f.net_due > Decimal('0.00')]

    @property
    def has_pending_submission(self):
        return self.submissions.filter(status='PENDING_VERIFICATION').exists()

    @property
    def pending_submission(self):
        return self.submissions.filter(status='PENDING_VERIFICATION').first()

    @property
    def under_review_amount(self):
        pending = self.submissions.filter(status='PENDING_VERIFICATION').aggregate(tot=models.Sum('amount'))['tot']
        return pending or Decimal('0.00')

    def update_status(self):
        net = self.net_due
        paid = self.amount_paid or Decimal('0.00')
        if net <= Decimal('0.00'):
            self.status = 'PAID'
        elif paid > Decimal('0.00'):
            self.status = 'PARTIAL'
        elif self.due_date and date.today() > self.due_date:
            self.status = 'OVERDUE'
        else:
            self.status = 'PENDING'

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} - {self.fee_head.name} | Net Due: ₹{self.net_due:.2f}"


class PaymentSubmission(TenantModel):
    """
    Student Payment Claim / Proof Submission.
    Student proof NEVER automatically makes a fee PAID.
    It initiates an approval workflow for school administrators.
    """
    PAYMENT_MODES = (
        ('UPI', 'UPI / QR Code (GPay, PhonePe, Paytm, etc.)'),
        ('BANK_TRANSFER', 'Bank Transfer / NEFT / IMPS / RTGS'),
        ('NET_BANKING', 'Net Banking'),
        ('CHEQUE', 'Cheque / Demand Draft'),
        ('CASH_DEPOSIT', 'Cash Deposit in School Bank A/C'),
        ('CARD', 'Debit / Credit Card'),
        ('OTHER', 'Other Payment Mode'),
    )

    STATUS_CHOICES = (
        ('PENDING_VERIFICATION', 'Pending Verification'),
        ('VERIFIED', 'Verified & Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled by Student'),
    )

    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_submissions")
    submission_no = models.CharField(max_length=64, unique=True, help_text="Generated claim ID, e.g. CLM-2026-000001")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODES, default='UPI')
    transaction_id = models.CharField(max_length=100, help_text="UTR / Transaction / Cheque / Reference ID")
    bank_name = models.CharField(max_length=100, blank=True, help_text="Bank / UPI App name")
    proof_file = models.FileField(upload_to=secure_fee_proof_path, blank=True, null=True)
    student_note = models.TextField(blank=True, help_text="Optional note from student/parent")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING_VERIFICATION')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="submitted_fee_claims")
    submitted_at = models.DateTimeField(auto_now_add=True)

    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_fee_claims")
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Claim #{self.submission_no} | ₹{self.amount} ({self.student.first_name}) - {self.get_status_display()}"


class FeePaymentQuerySet(models.QuerySet):
    def delete(self):
        raise PermissionDenied("FeePayment records are permanent financial entries and cannot be bulk deleted. Use payment reversal / void workflow instead.")


class FeePaymentTenantManager(TenantManager):
    def get_queryset(self):
        qs = FeePaymentQuerySet(self.model, using=self._db)
        current_school = get_current_school()
        if current_school:
            return qs.filter(school=current_school)
        return qs


class FeePaymentAllManager(models.Manager):
    def get_queryset(self):
        return FeePaymentQuerySet(self.model, using=self._db)


class FeePayment(TenantModel):
    """
    Official Verified Fee Payment Ledger Entry.
    Only created after administrator verification or direct in-person authorized counter collection.
    """
    MODE_CHOICES = (
        ('CASH', 'Cash Counter Collection'),
        ('UPI', 'UPI / QR Code'),
        ('BANK_TRANSFER', 'Bank Transfer / NEFT / IMPS'),
        ('ONLINE', 'Online Payment Gateway'),
        ('CHEQUE', 'Cheque / Bank Draft'),
        ('CARD', 'Debit / Credit Card'),
        ('OTHER', 'Other'),
    )

    STATUS_CHOICES = (
        ('VERIFIED', 'Verified / Active'),
        ('REVERSED', 'Reversed / Voided'),
        ('REFUNDED', 'Refunded'),
    )

    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name="payments")
    submission = models.OneToOneField(
        PaymentSubmission, on_delete=models.SET_NULL, null=True, blank=True, related_name="official_payment"
    )
    receipt_no = models.CharField(max_length=100, unique=True, help_text="e.g. REC-2026-000001")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(max_length=30, choices=MODE_CHOICES, default='CASH')
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Transaction Ref / Cheque No.")
    remarks = models.CharField(max_length=255, blank=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VERIFIED')
    reversal_reason = models.TextField(blank=True)
    reversed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reversed_payments")
    reversed_at = models.DateTimeField(null=True, blank=True)

    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    objects = FeePaymentTenantManager()
    all_objects = FeePaymentAllManager()

    class Meta:
        ordering = ['-payment_date']

    def recalculate_fee_ledger(self):
        """Recalculate parent student fee paid amount based only on active VERIFIED payments minus processed refunds."""
        verified_sum = self.student_fee.payments.filter(status='VERIFIED').aggregate(tot=models.Sum('amount_paid'))['tot'] or Decimal('0.00')
        refunded_sum = PaymentRefund.objects.filter(
            payment__student_fee=self.student_fee, status='PROCESSED'
        ).aggregate(tot=models.Sum('amount'))['tot'] or Decimal('0.00')
        net_paid = max(Decimal('0.00'), verified_sum - refunded_sum)
        self.student_fee.amount_paid = net_paid
        self.student_fee.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.recalculate_fee_ledger()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("FeePayment records are permanent financial entries and cannot be hard deleted. Use payment reversal / void workflow instead.")

    def __str__(self):
        return f"Receipt #{self.receipt_no} | ₹{self.amount_paid} ({self.student_fee.student.first_name})"


class FeeAdjustment(TenantModel):
    """
    Official Audit-tracked Fee Adjustments, Discounts, Fines or Corrections.
    Prevents silent alteration of historical fee balances.
    """
    ADJUSTMENT_TYPES = (
        ('DISCOUNT', 'Discount / Concession / Scholarship'),
        ('FINE', 'Late Fine / Penalty'),
        ('CORRECTION', 'Ledger Correction / Balance Fix'),
        ('WAIVER', 'Special Waiver'),
    )

    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=30, choices=ADJUSTMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Adjustment amount")
    reason = models.TextField(help_text="Mandatory detailed explanation for this adjustment")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_adjustment_type_display()} ₹{self.amount} for {self.student_fee.student.first_name}"


class PaymentRefund(TenantModel):
    """
    Payment Refund and Reversal Management.
    """
    STATUS_CHOICES = (
        ('REQUESTED', 'Refund Requested'),
        ('APPROVED', 'Refund Approved'),
        ('PROCESSED', 'Refund Processed / Completed'),
        ('REJECTED', 'Refund Rejected'),
    )

    payment = models.ForeignKey(FeePayment, on_delete=models.CASCADE, related_name="refunds")
    refund_no = models.CharField(max_length=64, unique=True, help_text="e.g. REF-2026-000001")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_mode = models.CharField(max_length=30, default='BANK_TRANSFER')
    reason = models.TextField(help_text="Reason for refund / chargeback")
    transaction_ref = models.CharField(max_length=100, blank=True, help_text="Bank refund transfer UTR")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='REQUESTED')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="refund_requests")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="refund_approvals")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Refund #{self.refund_no} | ₹{self.amount} for Receipt #{self.payment.receipt_no}"


class DailyFeeClosing(TenantModel):
    """
    Daily Fee Closing Report for Counter & Digital Collections.
    """
    closing_date = models.DateField()
    cash_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    upi_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    bank_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cheque_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    online_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    other_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_collected = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_refunded = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_closing = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('school', 'closing_date')
        ordering = ['-closing_date']

    def __str__(self):
        return f"Daily Closing: {self.closing_date} | Total ₹{self.total_collected:.2f} ({self.school.code if self.school_id else ''})"


class FeeAuditLogQuerySet(models.QuerySet):
    def delete(self):
        raise PermissionDenied("FeeAuditLog bulk deletion is strictly forbidden.")

    def update(self, **kwargs):
        raise PermissionDenied("FeeAuditLog bulk updates are strictly forbidden.")


class FeeAuditLogTenantManager(TenantManager):
    def get_queryset(self):
        qs = FeeAuditLogQuerySet(self.model, using=self._db)
        current_school = get_current_school()
        if current_school:
            return qs.filter(school=current_school)
        return qs


class FeeAuditLogAllManager(models.Manager):
    def get_queryset(self):
        return FeeAuditLogQuerySet(self.model, using=self._db)


class FeeAuditLog(TenantModel):
    """
    Immutable Application-Level Financial Audit Trail (OWASP & RBI Compliance).
    Entries can NEVER be modified or deleted, preserving forensic transaction history.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=60, help_text="e.g. PAYMENT_CLAIM_SUBMITTED, PAYMENT_APPROVED, PAYMENT_REJECTED, PAYMENT_REVERSED, FEE_ADJUSTMENT, REFUND_PROCESSED")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    student_fee = models.ForeignKey(StudentFee, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(FeePayment, on_delete=models.SET_NULL, null=True, blank=True)
    submission = models.ForeignKey(PaymentSubmission, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FeeAuditLogTenantManager()
    all_objects = FeeAuditLogAllManager()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionDenied("FeeAuditLog entries are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("FeeAuditLog entries are permanent and cannot be deleted.")

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.action} by {self.user.username if self.user else 'System'} - ₹{self.amount or 0}"
