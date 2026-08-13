from django.db import models
from accounts.models import TenantModel

class Class(TenantModel):
    CLASS_CHOICES = (
        ('Nursery', 'Nursery'),
        ('LKG', 'LKG'),
        ('UKG', 'UKG'),
        ('Class 1', 'Class 1'),
        ('Class 2', 'Class 2'),
        ('Class 3', 'Class 3'),
        ('Class 4', 'Class 4'),
        ('Class 5', 'Class 5'),
        ('Class 6', 'Class 6'),
        ('Class 7', 'Class 7'),
        ('Class 8', 'Class 8'),
        ('Class 9', 'Class 9'),
        ('Class 10', 'Class 10'),
        ('Class 11', 'Class 11'),
        ('Class 12', 'Class 12'),
    )

    name = models.CharField(max_length=50, choices=CLASS_CHOICES)
    numeric_value = models.IntegerField(default=1, help_text="Numeric order for sorting/promotion (e.g. Nursery=-2, 1=1, 12=12)")

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ['numeric_value', 'name']

    def __str__(self):
        return f"{self.name} ({self.school.code})"


class Section(TenantModel):
    STREAM_CHOICES = (
        ('General', 'General'),
        ('Science', 'Science'),
        ('Commerce', 'Commerce'),
        ('Arts', 'Arts / Humanities'),
    )

    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=20, help_text="e.g. A, B, C or Science-A")
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES, default='General')

    class Meta:
        ordering = ['class_level', 'name']

    def __str__(self):
        return f"{self.class_level.name} - {self.name} ({self.stream})"


class Subject(TenantModel):
    TYPE_CHOICES = (
        ('THEORY', 'Theory'),
        ('PRACTICAL', 'Practical'),
        ('BOTH', 'Theory & Practical'),
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, blank=True)
    subject_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='THEORY')
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    pass_marks = models.DecimalField(max_digits=5, decimal_places=2, default=33.00)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code or 'No Code'})"


class Timetable(TenantModel):
    DAYS = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    )

    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="timetables")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="timetables")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher_user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'TEACHER'})
    day = models.CharField(max_length=15, choices=DAYS)
    period_number = models.PositiveIntegerField(default=1)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day', 'period_number']

    def __str__(self):
        return f"{self.class_level.name}-{self.section.name} | {self.day} P{self.period_number} : {self.subject.name}"
