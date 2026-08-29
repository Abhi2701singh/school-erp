from django import forms
from examinations.models import Exam, MarksEntry

class ExamForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            from academics.models import Class
            self.fields['class_level'].queryset = Class.objects.filter(school=school)

    class Meta:
        model = Exam
        fields = ['name', 'exam_type', 'class_level', 'start_date', 'end_date', 'is_published']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Half Yearly Examination 2026'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
