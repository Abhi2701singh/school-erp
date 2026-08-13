from django.contrib import admin
from schools.models import School, AcademicSession, Notice

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'phone', 'email', 'principal_name', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'email', 'principal_name')
    list_filter = ('is_active',)

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'start_date', 'end_date', 'is_current')
    list_filter = ('school', 'is_current')
    search_fields = ('name', 'school__name')

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'target_role', 'is_active', 'created_at')
    list_filter = ('school', 'target_role', 'is_active')
    search_fields = ('title', 'content')
