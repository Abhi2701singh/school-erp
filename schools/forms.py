import re
from django import forms
from django.utils.text import slugify
from schools.models import School, AcademicSession, Notice

class SchoolForm(forms.ModelForm):
    code = forms.CharField(
        required=False,
        label="School Code",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DPS_DELHI (Auto-generated if left empty)'})
    )
    admin_username = forms.CharField(
        required=False,
        label="Admin Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. admin_dps (Auto-generated if left empty)'})
    )
    admin_password = forms.CharField(
        required=False,
        label="Admin Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Password@123 (Defaults to Password@123)'})
    )

    class Meta:
        model = School
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Delhi Public School'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full address / location (optional)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +91 9876543210 (optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. contact@dps.edu (optional)'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g. https://www.dps.edu (optional)'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dr. Rajesh Sharma (optional)'}),
            'affiliation_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CBSE/AFF/2025/01 (optional)'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2005 (optional)'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'online_payments_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'razorpay_key_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'rzp_live_... or rzp_test_...'}),
            'razorpay_key_secret': forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}),
            'razorpay_webhook_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'school@upi'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}),
            'bank_account_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'bank_ifsc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IFSC Code'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        name = self.cleaned_data.get('name', '')
        if not code:
            base_slug = slugify(name).upper().replace('-', '_') if name else "SCH"
            base_slug = base_slug[:30] if base_slug else "SCH"
            code = base_slug
        else:
            code = re.sub(r'[^A-Za-z0-9_]', '_', code.strip().upper())[:50]

        # Ensure uniqueness across other schools
        instance_pk = self.instance.pk if self.instance else None
        candidate = code
        counter = 1
        while School.objects.filter(code=candidate).exclude(pk=instance_pk).exists():
            candidate = f"{code[:40]}_{counter}"
            counter += 1

        return candidate


class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-2026'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'target_role', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Diwali Vacation Notice'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write complete notice details here...'}),
            'target_role': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SchoolPaymentGatewayForm(forms.ModelForm):
    razorpay_key_secret = forms.CharField(
        required=False,
        label="Razorpay Key Secret",
        widget=forms.PasswordInput(render_value=True, attrs={
            'class': 'form-control',
            'placeholder': 'Enter Key Secret from Razorpay Dashboard'
        }),
        help_text="Keep this secret confidential. It is used to securely verify student fee payments."
    )

    class Meta:
        model = School
        fields = [
            'online_payments_enabled',
            'razorpay_key_id',
            'razorpay_key_secret',
            'razorpay_webhook_secret',
            'upi_id',
            'bank_name',
            'bank_account_no',
            'bank_ifsc',
        ]
        widgets = {
            'online_payments_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'razorpay_key_id': forms.TextInput(attrs={'class': 'form-control font-monospace', 'placeholder': 'rzp_live_... or rzp_test_...'}),
            'razorpay_webhook_secret': forms.TextInput(attrs={'class': 'form-control font-monospace', 'placeholder': 'Optional webhook secret'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control font-monospace', 'placeholder': 'e.g. dps.school@upi'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bank of Baroda'}),
            'bank_account_no': forms.TextInput(attrs={'class': 'form-control font-monospace', 'placeholder': 'e.g. 99281002938491'}),
            'bank_ifsc': forms.TextInput(attrs={'class': 'form-control font-monospace text-uppercase', 'placeholder': 'e.g. BARB0KUSHIN'}),
        }


