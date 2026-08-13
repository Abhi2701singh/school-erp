from django import forms
from academics.models import Class, Section, Subject, Timetable

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'numeric_value']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-select'}),
            'numeric_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ordering integer (e.g. 1 for Class 1)'}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['class_level', 'name', 'stream']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section Name e.g. A, B, Science-A'}),
            'stream': forms.Select(attrs={'class': 'form-select'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'subject_type', 'max_marks', 'pass_marks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mathematics'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MATH101'}),
            'subject_type': forms.Select(attrs={'class': 'form-select'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'pass_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['class_level', 'section', 'subject', 'teacher_user', 'day', 'period_number', 'start_time', 'end_time']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher_user': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'period_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
