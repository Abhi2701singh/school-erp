from django import forms
from fees.models import FeeHead, FeeStructure, FeePayment, StudentFee

class FeeHeadForm(forms.ModelForm):
    class Meta:
        model = FeeHead
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tuition Fee'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['class_level', 'fee_head', 'amount', 'frequency', 'due_date']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'fee_head': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CollectFeeForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['amount_paid', 'payment_mode', 'transaction_id', 'remarks']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ref / Cheque / UPI ID'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
        }
