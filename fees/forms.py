import os
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from fees.models import (
    FeeHead, FeeStructure, FeePayment, StudentFee,
    PaymentSubmission, FeeAdjustment, PaymentRefund, DailyFeeClosing
)


ALLOWED_PROOF_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf', '.webp']
ALLOWED_PROOF_MIME_TYPES = ['image/jpeg', 'image/png', 'application/pdf', 'image/webp']
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class FeeHeadForm(forms.ModelForm):
    class Meta:
        model = FeeHead
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tuition Fee'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional details about this fee head'}),
        }


class FeeStructureForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            from academics.models import Class
            self.fields['class_level'].queryset = Class.objects.filter(school=school)
            self.fields['fee_head'].queryset = FeeHead.objects.filter(school=school)

    class Meta:
        model = FeeStructure
        fields = ['class_level', 'fee_head', 'amount', 'frequency', 'due_date']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'fee_head': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in ₹'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CollectFeeForm(forms.ModelForm):
    """Direct Counter Payment Form for Admins & Accountants."""
    class Meta:
        model = FeePayment
        fields = ['amount_paid', 'payment_mode', 'transaction_id', 'remarks']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ref / Cheque / UTR ID (leave blank for Cash)'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks/notes'}),
        }

    def clean_amount_paid(self):
        amount = self.cleaned_data.get('amount_paid')
        if amount is None or amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")
        return amount


class PaymentClaimSubmissionForm(forms.ModelForm):
    """
    Student Payment Proof / Claim Submission Form.
    Includes file validation, duplicate transaction prevention, and overpayment checks.
    """
    class Meta:
        model = PaymentSubmission
        fields = ['amount', 'payment_date', 'payment_mode', 'transaction_id', 'bank_name', 'proof_file', 'student_note']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount paid in ₹', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UTR / Transaction / Reference / Cheque ID'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. State Bank of India / Google Pay / HDFC'}),
            'proof_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png,.pdf,.webp'}),
            'student_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional message or details for administrator'}),
        }

    def __init__(self, *args, student_fee=None, school=None, **kwargs):
        self.student_fee = student_fee
        self.school = school
        super().__init__(*args, **kwargs)
        if not self.initial.get('payment_date'):
            self.initial['payment_date'] = date.today().isoformat()
        if student_fee:
            self.fields['amount'].help_text = f"Current Outstanding Net Due: ₹{student_fee.net_due:.2f}"

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise ValidationError("Payment amount must be strictly greater than zero.")

        if self.student_fee:
            net_due = self.student_fee.net_due
            if amount > net_due:
                raise ValidationError(
                    f"Submitted amount (₹{amount:.2f}) exceeds current outstanding balance (₹{net_due:.2f}). Overpayment is not permitted."
                )
        return amount

    def clean_payment_date(self):
        payment_date = self.cleaned_data.get('payment_date')
        if payment_date and payment_date > date.today():
            raise ValidationError("Payment date cannot be in the future.")
        return payment_date

    def clean_transaction_id(self):
        tx_id = self.cleaned_data.get('transaction_id', '').strip()
        if not tx_id:
            raise ValidationError("Transaction reference / UTR / Cheque number is required for verification.")

        # Check duplicate submission in active/pending/verified claims
        school = self.school or (self.student_fee.school if self.student_fee else None)
        if school:
            existing_claim = PaymentSubmission.objects.filter(
                school=school,
                transaction_id__iexact=tx_id,
                status__in=['PENDING_VERIFICATION', 'VERIFIED']
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if existing_claim:
                raise ValidationError("This transaction reference / UTR has already been submitted and is currently pending review or already verified.")

            existing_payment = FeePayment.objects.filter(
                school=school,
                transaction_id__iexact=tx_id,
                status='VERIFIED'
            ).exists()

            if existing_payment:
                raise ValidationError("This transaction reference has already been credited and issued a verified receipt.")

        return tx_id

    def clean_proof_file(self):
        proof = self.cleaned_data.get('proof_file')
        if proof:
            # File size limit check
            if proof.size > MAX_FILE_SIZE_BYTES:
                raise ValidationError("Payment proof file size cannot exceed 5MB.")

            # Extension check
            ext = os.path.splitext(proof.name)[1].lower()
            if ext not in ALLOWED_PROOF_EXTENSIONS:
                raise ValidationError(f"Invalid file type ({ext}). Allowed formats: JPG, PNG, PDF, WEBP.")

            # Content type check if available
            if hasattr(proof, 'content_type') and proof.content_type:
                if proof.content_type not in ALLOWED_PROOF_MIME_TYPES:
                    raise ValidationError("Uploaded file MIME type is not allowed for security reasons.")

        return proof


class PaymentApprovalForm(forms.Form):
    """Admin double-confirmation approval form."""
    verified_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    payment_mode = forms.ChoiceField(
        choices=FeePayment.MODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    admin_notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional approval remarks / ledger notes'})
    )
    confirm_checkbox = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must confirm that you have verified the payment and bank credit.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class PaymentRejectionForm(forms.Form):
    """Admin payment claim rejection form."""
    rejection_reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please enter the specific reason for rejecting this payment proof (e.g. UTR not matching bank statement, incorrect amount)...'}),
        help_text="Rejection reason will be visible to the student/parent."
    )


class FeeAdjustmentForm(forms.ModelForm):
    """Form to create an audit-tracked fee adjustment."""
    class Meta:
        model = FeeAdjustment
        fields = ['adjustment_type', 'amount', 'reason']
        widgets = {
            'adjustment_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in ₹', 'step': '0.01'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mandatory detailed justification (e.g. Principal approved 10% scholarship, sibling concession, late fine)...'}),
        }

    def __init__(self, *args, student_fee=None, **kwargs):
        self.student_fee = student_fee
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amt = self.cleaned_data.get('amount')
        if amt is None or amt <= 0:
            raise ValidationError("Adjustment amount must be greater than zero.")
        return amt

    def clean_reason(self):
        reason = self.cleaned_data.get('reason', '').strip()
        if len(reason) < 5:
            raise ValidationError("Please provide a meaningful reason of at least 5 characters.")
        return reason

    def clean(self):
        cleaned_data = super().clean()
        adj_type = cleaned_data.get('adjustment_type')
        amt = cleaned_data.get('amount')
        if self.student_fee and adj_type in ['DISCOUNT', 'WAIVER', 'CORRECTION'] and amt:
            if amt > self.student_fee.net_due:
                self.add_error('amount', f"Discount / Concession amount (₹{amt:.2f}) cannot exceed current outstanding balance (₹{self.student_fee.net_due:.2f}).")
        return cleaned_data


class PaymentReversalForm(forms.Form):
    """Void / Reverse a verified payment."""
    reversal_reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mandatory reason for reversing this payment (e.g. Cheque bounced, accidental double entry, chargeback)...'}),
    )


class PaymentRefundForm(forms.ModelForm):
    """Form to initiate / request a refund."""
    class Meta:
        model = PaymentRefund
        fields = ['amount', 'refund_mode', 'reason', 'transaction_ref']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Refund amount in ₹'}),
            'refund_mode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bank Transfer / UPI / Cheque'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed reason for refund (e.g. Student transferred, duplicate fee refund)...'}),
            'transaction_ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank transfer UTR / Cheque Ref'}),
        }

    def __init__(self, *args, payment=None, **kwargs):
        self.payment = payment
        super().__init__(*args, **kwargs)
        if payment:
            from django.db.models import Sum
            from decimal import Decimal
            existing_refunds = self.payment.refunds.exclude(status='REJECTED').exclude(
                pk=self.instance.pk if self.instance else None
            ).aggregate(tot=Sum('amount'))['tot'] or Decimal('0.00')
            remaining = max(Decimal('0.00'), payment.amount_paid - existing_refunds)
            self.fields['amount'].help_text = f"Maximum refundable amount: ₹{remaining:.2f} (Verified: ₹{payment.amount_paid:.2f}, Prior Refunds: ₹{existing_refunds:.2f})"

    def clean_amount(self):
        amt = self.cleaned_data.get('amount')
        if amt is None or amt <= 0:
            raise ValidationError("Refund amount must be greater than zero.")
        if self.payment:
            from django.db.models import Sum
            from decimal import Decimal
            existing_refunds = self.payment.refunds.exclude(status='REJECTED').exclude(
                pk=self.instance.pk if self.instance else None
            ).aggregate(tot=Sum('amount'))['tot'] or Decimal('0.00')
            max_allowed = self.payment.amount_paid - existing_refunds
            if amt > max_allowed:
                raise ValidationError(
                    f"Refund amount (₹{amt:.2f}) exceeds remaining refundable balance (₹{max_allowed:.2f}). "
                    f"Prior active/completed refunds: ₹{existing_refunds:.2f}."
                )
        return amt


class DailyFeeClosingForm(forms.ModelForm):
    class Meta:
        model = DailyFeeClosing
        fields = ['closing_date', 'notes']
        widgets = {
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional closing remarks / cash physical count confirmation'}),
        }
