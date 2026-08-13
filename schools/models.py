from django.db import models
from django.utils.translation import gettext_lazy as _

class School(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("School Name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("School Code / Slug"))
    logo = models.ImageField(upload_to="school_logos/", null=True, blank=True)
    address = models.TextField(verbose_name=_("Address"))
    phone = models.CharField(max_length=20, verbose_name=_("Contact Phone"))
    email = models.EmailField(verbose_name=_("Contact Email"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    principal_name = models.CharField(max_length=150, blank=True, verbose_name=_("Principal Name"))
    affiliation_no = models.CharField(max_length=100, blank=True, verbose_name=_("Affiliation No."))
    established_year = models.IntegerField(null=True, blank=True, verbose_name=_("Established Year"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active Status"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("School")
        verbose_name_plural = _("Schools")

    def __str__(self):
        return f"{self.name} ({self.code})"


class AcademicSession(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_sessions")
    name = models.CharField(max_length=50, help_text=_("e.g. 2025-2026"))
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ('school', 'name')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.school.name} - {self.name}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other sessions for this school to False
            AcademicSession.objects.filter(school=self.school, is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Notice(models.Model):
    ROLE_CHOICES = (
        ('ALL', _('All (Entire School)')),
        ('TEACHER', _('Teachers Only')),
        ('STUDENT', _('Students Only')),
        ('PARENT', _('Parents Only')),
    )

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="notices")
    title = models.CharField(max_length=255)
    content = models.TextField()
    target_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ALL')
    attachment = models.FileField(upload_to="notices/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.school.code}] {self.title}"
