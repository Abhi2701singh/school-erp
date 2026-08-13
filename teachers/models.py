from django.db import models
from accounts.models import TenantModel, User
from academics.models import Class, Section, Subject

class Teacher(TenantModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    employee_id = models.CharField(max_length=50)
    qualification = models.CharField(max_length=150, help_text="e.g. M.Sc. Physics, B.Ed.")
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    joining_date = models.DateField()

    assigned_classes = models.ManyToManyField(Class, blank=True, related_name="assigned_teachers")
    assigned_sections = models.ManyToManyField(Section, blank=True, related_name="assigned_teachers")
    assigned_subjects = models.ManyToManyField(Subject, blank=True, related_name="assigned_teachers")

    class Meta:
        ordering = ['user__first_name', 'employee_id']
        unique_together = ('school', 'employee_id')

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"{full_name} ({self.employee_id})"
