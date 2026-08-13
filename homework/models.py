from django.db import models
from accounts.models import TenantModel, User
from academics.models import Class, Section, Subject

class Homework(TenantModel):
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="homeworks")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="homeworks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to="homework_files/", null=True, blank=True)
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.title} - {self.class_level.name}-{self.section.name} ({self.subject.name})"


class StudyMaterial(TenantModel):
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="study_materials")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="study_materials/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.class_level.name} | {self.subject.name})"
