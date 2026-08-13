from django.contrib import admin
from academics.models import Class, Section, Subject, Timetable

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'numeric_value')
    list_filter = ('school',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_level', 'stream', 'school')
    list_filter = ('school', 'class_level', 'stream')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'subject_type', 'max_marks', 'pass_marks', 'school')
    list_filter = ('school', 'subject_type')
    search_fields = ('name', 'code')

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'section', 'subject', 'day', 'period_number', 'start_time', 'end_time', 'school')
    list_filter = ('school', 'day', 'class_level')
