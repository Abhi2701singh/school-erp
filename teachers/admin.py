from django.contrib import admin
from teachers.models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'phone', 'qualification', 'joining_date', 'school')
    list_filter = ('school',)
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'phone')
