from django.db import models
from accounts.models import TenantModel, User
from schools.models import AcademicSession
from academics.models import Class, Section
from students.models import Student
from teachers.models import Teacher

class StudentAttendance(TenantModel):
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('LE', 'Leave'),
        ('H', 'Half Day'),
    )

    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    date = models.DateField()
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='P')
    remarks = models.CharField(max_length=255, blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('school', 'academic_session', 'date', 'student')
        ordering = ['-date', 'class_level', 'section', 'student__roll_no']

    def __str__(self):
        return f"{self.date} | {self.student.first_name} : {self.get_status_display()}"


class TeacherAttendance(TenantModel):
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('LE', 'Leave'),
    )

    date = models.DateField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='P')
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('school', 'date', 'teacher')
        ordering = ['-date', 'teacher']

    def __str__(self):
        return f"{self.date} | {self.teacher.user.get_full_name()} : {self.get_status_display()}"
