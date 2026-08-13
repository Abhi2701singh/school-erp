from django.contrib import admin
from homework.models import Homework, StudyMaterial

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_level', 'section', 'subject', 'assigned_date', 'due_date', 'school')
    list_filter = ('school', 'class_level', 'subject')
    search_fields = ('title', 'description')

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_level', 'subject', 'uploaded_at', 'school')
    list_filter = ('school', 'class_level', 'subject')
    search_fields = ('title', 'description')
