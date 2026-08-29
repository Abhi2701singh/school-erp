from django import forms
from students.models import Student, StudentDocument
from schools.models import AcademicSession
from academics.models import Class, Section

class StudentAdmissionForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['academic_session'].queryset = AcademicSession.objects.filter(school=school)
            self.fields['current_class'].queryset = Class.objects.filter(school=school)
            self.fields['current_section'].queryset = Section.objects.filter(school=school)
            
            # If only one active session exists, set it as initial
            active_session = AcademicSession.objects.filter(school=school, is_current=True).first()
            if active_session and not self.initial.get('academic_session'):
                self.fields['academic_session'].initial = active_session

        self.fields['admission_no'].required = False
        self.fields['admission_date'].required = False
        self.fields['address'].required = False
        self.fields['father_name'].required = False
        self.fields['parent_phone'].required = False
        self.fields['gender'].initial = 'M'

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
            'admission_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to auto-generate'}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 101'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name / Surname'}),
            'dob': forms.DateInput(attrs={'class': 'form-control dob-picker', 'placeholder': 'Select Date of Birth (YYYY-MM-DD)'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. O+, A+, B+'}),
            'govt_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aadhaar / National ID'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential Address'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control admission-date-picker', 'placeholder': 'Admission Date (YYYY-MM-DD)'}),
            'academic_session': forms.Select(attrs={'class': 'form-select'}),
            'current_class': forms.Select(attrs={'class': 'form-select'}),
            'current_section': forms.Select(attrs={'class': 'form-select'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Full Name"}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Name"}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Guardian's Name (Optional)"}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'parent_occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}),
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
