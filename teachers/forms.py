from django import forms
from teachers.models import Teacher
from accounts.models import User

class TeacherForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if unchanged'}), required=False)

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            from academics.models import Class, Section, Subject
            self.fields['assigned_classes'].queryset = Class.objects.filter(school=school)
            self.fields['assigned_sections'].queryset = Section.objects.filter(school=school)
            self.fields['assigned_subjects'].queryset = Subject.objects.filter(school=school)

    class Meta:
        model = Teacher
        fields = ['employee_id', 'qualification', 'phone', 'address', 'joining_date', 'assigned_classes', 'assigned_sections', 'assigned_subjects']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EMP2026-01'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. M.Sc. Math, B.Ed.'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_classes': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'assigned_sections': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'assigned_subjects': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }
