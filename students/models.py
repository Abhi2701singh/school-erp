from django.db import models
from accounts.models import TenantModel, User
from schools.models import AcademicSession
from academics.models import Class, Section

class Student(TenantModel):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PROMOTED', 'Promoted'),
        ('GRADUATED', 'Graduated'),
        ('TRANSFERRED', 'Transferred'),
        ('INACTIVE', 'Inactive'),
    )

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_profile")
    admission_no = models.CharField(max_length=50)
    roll_no = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=10, blank=True)
    photo = models.ImageField(upload_to="student_photos/", null=True, blank=True)
    govt_id = models.CharField(max_length=50, blank=True, verbose_name="Aadhaar / National ID")
    address = models.TextField()
    admission_date = models.DateField()
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="students")
    current_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="students")
    current_section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="students")

    # Parent / Guardian details
    father_name = models.CharField(max_length=150)
    mother_name = models.CharField(max_length=150, blank=True)
    guardian_name = models.CharField(max_length=150, blank=True)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True)
    parent_occupation = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['current_class', 'current_section', 'roll_no', 'first_name']
        unique_together = ('school', 'admission_no')

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return f"{full_name} (Adm: {self.admission_no} | Class: {self.current_class.name}-{self.current_section.name})"


class ParentProfile(TenantModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    students = models.ManyToManyField(Student, related_name="parents")
    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)
    primary_phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Parent: {self.father_name or self.user.username} ({self.primary_phone})"


class StudentDocument(TenantModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=150, help_text="e.g. Birth Certificate, Transfer Certificate")
    document_file = models.FileField(upload_to="student_docs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.title}"
