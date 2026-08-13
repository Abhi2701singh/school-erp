from django.db import models
from accounts.models import TenantModel, User
from schools.models import AcademicSession
from academics.models import Class, Subject
from students.models import Student

class Exam(TenantModel):
    EXAM_TYPES = (
        ('UNIT_TEST', 'Unit Test'),
        ('MONTHLY', 'Monthly Test'),
        ('HALF_YEARLY', 'Half Yearly Examination'),
        ('PRE_BOARD', 'Pre-Board Examination'),
        ('ANNUAL', 'Annual Examination'),
        ('CUSTOM', 'Custom Assessment'),
    )

    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="exams")
    name = models.CharField(max_length=150, help_text="e.g. Term-1 Half Yearly Exam")
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='UNIT_TEST')
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="exams")
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False, verbose_name="Publish Result")

    class Meta:
        ordering = ['-start_date', 'name']

    def __str__(self):
        return f"{self.name} - {self.class_level.name} ({self.academic_session.name})"


class MarksEntry(TenantModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="marks_entries")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
    theory_marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    practical_marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    grade = models.CharField(max_length=5, blank=True)
    is_pass = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, blank=True)
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('school', 'exam', 'student', 'subject')
        ordering = ['student', 'subject']

    def calculate_results(self):
        self.total_marks_obtained = self.theory_marks_obtained + self.practical_marks_obtained
        max_m = float(self.subject.max_marks or 100)
        pass_m = float(self.subject.pass_marks or 33)
        total_m = float(self.total_marks_obtained)
        percentage = (total_m / max_m) * 100.0 if max_m > 0 else 0.0

        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C+'
        elif percentage >= 40:
            self.grade = 'C'
        elif percentage >= 33:
            self.grade = 'D'
        else:
            self.grade = 'F'

        self.is_pass = total_m >= pass_m

    def save(self, *args, **kwargs):
        self.calculate_results()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} | {self.subject.name} : {self.total_marks_obtained} ({self.grade})"
