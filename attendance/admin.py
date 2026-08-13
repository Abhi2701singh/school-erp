from django.contrib import admin
from attendance.models import StudentAttendance, TeacherAttendance

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'class_level', 'section', 'status', 'school')
    list_filter = ('school', 'status', 'class_level', 'date')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_no')

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'teacher', 'status', 'school')
    list_filter = ('school', 'status', 'date')
