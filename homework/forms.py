from django import forms
from homework.models import Homework, StudyMaterial

class HomeworkForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            from academics.models import Class, Section, Subject
            self.fields['class_level'].queryset = Class.objects.filter(school=school)
            self.fields['section'].queryset = Section.objects.filter(school=school)
            self.fields['subject'].queryset = Subject.objects.filter(school=school)

    class Meta:
        model = Homework
        fields = ['class_level', 'section', 'subject', 'title', 'description', 'attachment', 'due_date']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Chapter 4 Exercise Questions'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class StudyMaterialForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            from academics.models import Class, Subject
            self.fields['class_level'].queryset = Class.objects.filter(school=school)
            self.fields['subject'].queryset = Subject.objects.filter(school=school)

    class Meta:
        model = StudyMaterial
        fields = ['class_level', 'subject', 'title', 'description', 'file']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Revision Notes Unit 2'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
