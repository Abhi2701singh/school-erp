from django import forms
from students.models import Student, StudentDocument
from schools.models import AcademicSession
from academics.models import Class, Section

class StudentAdmissionForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'admission_no', 'roll_no', 'first_name', 'last_name', 'dob', 'gender',
            'blood_group', 'govt_id', 'photo', 'address', 'admission_date',
            'academic_session', 'current_class', 'current_section',
            'father_name', 'mother_name', 'guardian_name', 'parent_phone',
            'parent_email', 'parent_occupation', 'status'
        ]
        widgets = {
            'admission_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ADM2026-001'}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 101'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. O+'}),
            'govt_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aadhaar / National ID'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'academic_session': forms.Select(attrs={'class': 'form-select'}),
            'current_class': forms.Select(attrs={'class': 'form-select'}),
            'current_section': forms.Select(attrs={'class': 'form-select'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parent_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ['title', 'document_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Birth Certificate'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
