from django.contrib import admin
from examinations.models import Exam, MarksEntry

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'class_level', 'academic_session', 'is_published', 'school')
    list_filter = ('school', 'exam_type', 'is_published')
    search_fields = ('name',)

@admin.register(MarksEntry)
class MarksEntryAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'subject', 'total_marks_obtained', 'grade', 'is_pass', 'school')
    list_filter = ('school', 'exam', 'grade', 'is_pass')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_no', 'subject__name')
