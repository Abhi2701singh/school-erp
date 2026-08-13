from django.contrib import admin
from students.models import Student, ParentProfile, StudentDocument

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_no', 'first_name', 'last_name', 'current_class', 'current_section', 'parent_phone', 'status', 'school')
    list_filter = ('school', 'current_class', 'status')
    search_fields = ('admission_no', 'first_name', 'last_name', 'parent_phone', 'govt_id')

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'father_name', 'mother_name', 'primary_phone', 'school')
    search_fields = ('father_name', 'primary_phone')

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'uploaded_at', 'school')
