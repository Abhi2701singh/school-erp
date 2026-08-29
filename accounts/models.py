import threading
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from schools.models import School

# Thread-local storage for current tenant school
_thread_locals = threading.local()

def get_current_school():
    return getattr(_thread_locals, 'school', None)

def set_current_school(school):
    _thread_locals.school = school


class TenantManager(models.Manager):
    """
    Manager that automatically filters querysets by the active tenant school
    unless superuser or explicit all_objects manager is used.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        current_school = get_current_school()
        if current_school:
            return qs.filter(school=current_school)
        return qs


class TenantModel(models.Model):
    """
    Abstract base model for multi-tenant models tied to a specific School.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="%(class)ss")

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.school_id:
            current_school = get_current_school()
            if current_school:
                self.school = current_school
        super().save(*args, **kwargs)


class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')
        SCHOOL_ADMIN = 'SCHOOL_ADMIN', _('School Admin')
        PRINCIPAL = 'PRINCIPAL', _('Principal')
        TEACHER = 'TEACHER', _('Teacher')
        ACCOUNTANT = 'ACCOUNTANT', _('Accountant')
        LIBRARIAN = 'LIBRARIAN', _('Librarian')
        STUDENT = 'STUDENT', _('Student')
        PARENT = 'PARENT', _('Parent')

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.SCHOOL_ADMIN)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name="users")
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)

    def is_super_admin(self):
        return self.role == self.Roles.SUPER_ADMIN or self.is_superuser

    def is_school_admin(self):
        return self.role in [self.Roles.SCHOOL_ADMIN, self.Roles.PRINCIPAL]

    def is_teacher_user(self):
        return self.role == self.Roles.TEACHER

    def is_student_user(self):
        return self.role == self.Roles.STUDENT

    def is_parent_user(self):
        return self.role == self.Roles.PARENT

    def __str__(self):
        role_label = self.get_role_display()
        school_label = self.school.name if self.school else "Global"
        return f"{self.get_full_name() or self.username} ({role_label} - {school_label})"
