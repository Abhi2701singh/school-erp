from django.db import models
from accounts.models import TenantModel, User
from schools.models import AcademicSession
from academics.models import Class
from students.models import Student

class FeeHead(TenantModel):
    name = models.CharField(max_length=100, help_text="e.g. Tuition Fee, Admission Fee, Exam Fee")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.school.code})"


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
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
    )

    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="student_fees")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['due_date', 'student']

    @property
    def net_due(self):
        return max(0.0, float(self.amount_due) - float(self.amount_discount) - float(self.amount_paid))

    def update_status(self):
        net = self.net_due
        if net <= 0:
            self.status = 'PAID'
        elif float(self.amount_paid) > 0:
            self.status = 'PARTIAL'
        else:
            self.status = 'PENDING'

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} - {self.fee_head.name} | Net Due: ₹{self.net_due:.2f}"


class FeePayment(TenantModel):
    MODE_CHOICES = (
        ('CASH', 'Cash'),
        ('ONLINE', 'Online Payment Gateway'),
        ('UPI', 'UPI / QR Code'),
        ('CHEQUE', 'Cheque / Bank Draft'),
    )

    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name="payments")
    receipt_no = models.CharField(max_length=100, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='CASH')
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Transaction Ref / Cheque No.")
    remarks = models.CharField(max_length=255, blank=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-payment_date']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update student_fee paid amount sum
        total_p = sum([p.amount_paid for p in self.student_fee.payments.all()])
        self.student_fee.amount_paid = total_p
        self.student_fee.save()

    def __str__(self):
        return f"Receipt #{self.receipt_no} | ₹{self.amount_paid} ({self.student_fee.student.first_name})"
