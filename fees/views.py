import os
import json
from datetime import date, datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseNotFound, FileResponse, Http404
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.conf import settings

from accounts.models import User
from schools.models import AcademicSession
from students.models import Student, ParentProfile
from academics.models import Class
from fees.models import (
    FeeHead, FeeStructure, StudentFee, PaymentSubmission,
    FeePayment, FeeAdjustment, PaymentRefund, DailyFeeClosing, FeeAuditLog
)
from fees.forms import (
    FeeHeadForm, FeeStructureForm, CollectFeeForm,
    PaymentClaimSubmissionForm, PaymentApprovalForm, PaymentRejectionForm,
    FeeAdjustmentForm, PaymentReversalForm, PaymentRefundForm, DailyFeeClosingForm
)
from fees.utils import (
    get_client_ip, generate_receipt_number, generate_claim_number,
    generate_refund_number, user_can_access_student, mask_student_name
)


# ==========================================
# 1. FEE STRUCTURE & ASSIGNMENT (STAFF)
# ==========================================

@login_required
def fee_structure_view(request):
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted to fee management staff.")
        return redirect('dashboard')

    fee_heads = FeeHead.objects.filter(school=request.school)
    structures = FeeStructure.objects.filter(school=request.school).select_related('class_level', 'fee_head')

    head_form = FeeHeadForm()
    struct_form = FeeStructureForm(school=request.school)

    if request.method == 'POST':
        if 'create_head' in request.POST:
            head_form = FeeHeadForm(request.POST)
            if head_form.is_valid():
                fh = head_form.save(commit=False)
                fh.school = request.school
                fh.save()
                messages.success(request, f"Fee Head '{fh.name}' created.")
                return redirect('fee_structure')
        elif 'create_struct' in request.POST:
            struct_form = FeeStructureForm(request.POST, school=request.school)
            if struct_form.is_valid():
                active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()
                if not active_session:
                    messages.error(request, "No active academic session found. Please activate a session first.")
                    return redirect('fee_structure')

                st = struct_form.save(commit=False)
                st.school = request.school
                st.academic_session = active_session
                st.save()
                messages.success(request, f"Fee structure for '{st.class_level.name} - {st.fee_head.name}' added.")
                return redirect('fee_structure')

    return render(request, 'fees/fee_structure.html', {
        'fee_heads': fee_heads,
        'structures': structures,
        'head_form': head_form,
        'struct_form': struct_form,
    })


@login_required
def assign_fees_view(request):
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()
        if not active_session:
            messages.error(request, "No active academic session found.")
            return redirect('fee_structure')

        structures = FeeStructure.objects.filter(school=request.school, class_level_id=class_id, academic_session=active_session)
        students = Student.objects.filter(school=request.school, current_class_id=class_id, status='ACTIVE')

        if not structures.exists():
            messages.warning(request, "No fee structures configured for the selected class in this academic session.")
            return redirect('fee_structure')

        assigned_count = 0
        with transaction.atomic():
            for student in students:
                for st in structures:
                    _, created = StudentFee.objects.get_or_create(
                        school=request.school,
                        academic_session=active_session,
                        student=student,
                        fee_head=st.fee_head,
                        due_date=st.due_date or active_session.end_date,
                        defaults={'amount_due': st.amount}
                    )
                    if created:
                        assigned_count += 1

            if assigned_count > 0:
                FeeAuditLog.objects.create(
                    school=request.school,
                    user=request.user,
                    action='FEES_BATCH_ASSIGNED',
                    ip_address=get_client_ip(request),
                    details={'class_id': class_id, 'assigned_count': assigned_count, 'session': active_session.name}
                )

        messages.success(request, f"Successfully assigned {assigned_count} fee entries to class students!")
        return redirect('fee_structure')

    return redirect('fee_structure')


# ==========================================
# 2. IN-PERSON COUNTER FEE COLLECTION (STAFF)
# ==========================================

@login_required
def collect_fee_view(request, student_id):
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted to authorized fee collectors.")
        return redirect('dashboard')

    student = get_object_or_404(Student, pk=student_id, school=request.school)
    student_fees = StudentFee.objects.filter(school=request.school, student=student).select_related('fee_head', 'academic_session')

    if request.method == 'POST':
        student_fee_id = request.POST.get('student_fee_id')
        student_fee = get_object_or_404(StudentFee, pk=student_fee_id, student=student, school=request.school)

        form = CollectFeeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount_paid']
            if amount > student_fee.net_due:
                messages.error(request, f"Amount entered (₹{amount:.2f}) exceeds current net due (₹{student_fee.net_due:.2f}).")
            else:
                with transaction.atomic():
                    receipt_no = generate_receipt_number(request.school)
                    payment = form.save(commit=False)
                    payment.school = request.school
                    payment.student_fee = student_fee
                    payment.receipt_no = receipt_no
                    payment.collected_by = request.user
                    payment.status = 'VERIFIED'
                    payment.save()

                    FeeAuditLog.objects.create(
                        school=request.school,
                        user=request.user,
                        action='PAYMENT_COLLECTED_COUNTER',
                        student=student,
                        student_fee=student_fee,
                        payment=payment,
                        amount=payment.amount_paid,
                        old_status='PENDING',
                        new_status='VERIFIED',
                        ip_address=get_client_ip(request),
                        details={
                            'receipt_no': receipt_no,
                            'payment_mode': payment.payment_mode,
                            'collected_by': request.user.username,
                        }
                    )

                messages.success(request, f"Fee payment recorded! Official Receipt #{receipt_no}")
                return redirect('fee_receipt', receipt_id=payment.pk)
    else:
        form = CollectFeeForm()

    return render(request, 'fees/collect_fee.html', {
        'student': student,
        'student_fees': student_fees,
        'form': form,
    })


@login_required
def fee_defaulters_view(request):
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted.")
        return redirect('dashboard')

    class_id = request.GET.get('class_id')
    pending_fees = StudentFee.objects.filter(
        school=request.school,
        status__in=['PENDING', 'PARTIAL', 'OVERDUE']
    ).select_related('student', 'fee_head', 'student__current_class', 'student__current_section')

    if class_id:
        pending_fees = pending_fees.filter(student__current_class_id=class_id)

    classes = Class.objects.filter(school=request.school)

    total_outstanding = sum([f.net_due for f in pending_fees], Decimal('0.00'))

    return render(request, 'fees/fee_defaulters.html', {
        'pending_fees': pending_fees,
        'classes': classes,
        'selected_class': class_id,
        'total_outstanding': total_outstanding,
    })


# ==========================================
# 3. STUDENT & PARENT FEE PORTAL ("MY FEES")
# ==========================================

@login_required
def my_fees_view(request):
    """
    Student / Parent Portal Fee Dashboard.
    Strictly isolated: Student only sees their own fees. Parent only sees linked children.
    """
    student = None
    linked_children = []

    if request.user.is_student_user():
        student = getattr(request.user, 'student_profile', None)
        if not student:
            messages.error(request, "No student profile is linked to your account.")
            return redirect('dashboard')
    elif request.user.is_parent_user():
        parent_profile = getattr(request.user, 'parent_profile', None)
        if parent_profile:
            linked_children = list(parent_profile.students.filter(school=request.school))
            requested_child_id = request.GET.get('student_id')
            if requested_child_id:
                student = next((c for c in linked_children if str(c.id) == str(requested_child_id)), None)
                if not student:
                    messages.error(request, "Unauthorized student selection.")
                    return redirect('my_fees')
            elif linked_children:
                student = linked_children[0]
        if not student:
            messages.error(request, "No linked students found for your parent account.")
            return redirect('dashboard')
    else:
        # Admins or teachers landing here get redirected to verification / structure
        if request.user.can_manage_fees():
            return redirect('fee_verifications')
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    # Security check: ensure student belongs to request.school
    if student.school_id != request.school.id:
        messages.error(request, "Tenant school mismatch.")
        return redirect('dashboard')

    student_fees = StudentFee.objects.filter(
        school=request.school, student=student
    ).select_related('fee_head', 'academic_session').prefetch_related('submissions')

    # Summary Metrics
    total_fee = sum([f.amount_due for f in student_fees], Decimal('0.00'))
    total_paid = sum([f.amount_paid for f in student_fees], Decimal('0.00'))
    total_discount = sum([f.amount_discount for f in student_fees], Decimal('0.00'))
    total_pending = sum([f.net_due for f in student_fees], Decimal('0.00'))
    total_under_review = sum([f.under_review_amount for f in student_fees], Decimal('0.00'))

    # Past Unpaid Arrears / Previous Dues Calculation
    today_dt = date.today()
    total_past_arrears = sum([f.net_due for f in student_fees if f.due_date and f.due_date < today_dt], Decimal('0.00'))
    current_fees_due = sum([f.net_due for f in student_fees if not f.due_date or f.due_date >= today_dt], Decimal('0.00'))

    # Payment Claims / Submissions
    submissions = PaymentSubmission.objects.filter(
        school=request.school, student=student
    ).select_related('student_fee__fee_head', 'official_payment').order_by('-submitted_at')

    # Official Verified Receipts
    verified_payments = FeePayment.objects.filter(
        school=request.school, student_fee__student=student, status='VERIFIED'
    ).select_related('student_fee__fee_head').order_by('-payment_date')

    return render(request, 'fees/my_fees.html', {
        'student': student,
        'linked_children': linked_children,
        'student_fees': student_fees,
        'submissions': submissions,
        'verified_payments': verified_payments,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'total_discount': total_discount,
        'total_pending': total_pending,
        'total_under_review': total_under_review,
        'total_past_arrears': total_past_arrears,
        'current_fees_due': current_fees_due,
    })


@login_required
def fee_challan_view(request, fee_id):
    """
    Generate Official Fee Challan / Proforma Invoice / Payment Slip.
    Displays current fee, itemized previous unpaid arrears, bank transfer details & QR instructions.
    """
    student_fee = get_object_or_404(
        StudentFee.objects.select_related('student', 'fee_head', 'academic_session', 'student__current_class', 'student__current_section', 'school'),
        pk=fee_id,
        school=request.school
    )

    if not user_can_access_student(request.user, student_fee.student):
        return HttpResponseForbidden("You do not have authorization to view this fee challan.")

    previous_arrears = student_fee.previous_arrears
    past_unpaid_items = student_fee.get_past_unpaid_fee_items()
    total_payable = student_fee.total_payable_with_arrears
    session_year = student_fee.academic_session.name[:4] if (student_fee.academic_session and student_fee.academic_session.name) else '2026'
    challan_no = f"CHL-{session_year}-{student_fee.pk:06d}"

    return render(request, 'fees/fee_challan.html', {
        'student_fee': student_fee,
        'student': student_fee.student,
        'previous_arrears': previous_arrears,
        'past_unpaid_items': past_unpaid_items,
        'total_payable': total_payable,
        'challan_no': challan_no,
        'issue_date': date.today(),
    })


@login_required
def claim_acknowledgement_view(request, submission_id):
    """
    Download/Print Payment Proof Submission Acknowledgement Slip.
    Issued immediately upon student submitting payment claim before admin verification.
    """
    submission = get_object_or_404(
        PaymentSubmission.objects.select_related('student', 'student_fee', 'student_fee__fee_head', 'student_fee__academic_session', 'student__current_class', 'student__current_section', 'school', 'official_payment'),
        pk=submission_id,
        school=request.school
    )

    if not user_can_access_student(request.user, submission.student):
        return HttpResponseForbidden("You do not have authorization to view this payment claim slip.")

    return render(request, 'fees/claim_acknowledgement.html', {
        'submission': submission,
        'student': submission.student,
        'student_fee': submission.student_fee,
    })


@login_required
def submit_payment_claim_view(request, fee_id):
    """
    Student / Parent submits payment claim proof.
    Strict OWASP IDOR, overpayment, and duplicate transaction checks.
    """
    student_fee = get_object_or_404(
        StudentFee.objects.select_related('student', 'fee_head', 'academic_session'),
        pk=fee_id,
        school=request.school
    )

    # IDOR Check: Ensure current user is the student or parent of this student
    if not user_can_access_student(request.user, student_fee.student):
        return HttpResponseForbidden("You do not have authorization to submit payment for this fee.")

    # Check if fee is already fully paid
    if student_fee.net_due <= 0:
        messages.info(request, "This fee entry is already fully paid.")
        return redirect('my_fees')

    # Check if an active pending claim is already under review
    if student_fee.has_pending_submission:
        messages.warning(
            request,
            "A payment claim for this fee is already under review by school administration. Please wait for verification."
        )
        return redirect('my_fees')

    previous_arrears = student_fee.previous_arrears
    past_unpaid_items = student_fee.get_past_unpaid_fee_items()
    total_payable = student_fee.total_payable_with_arrears

    if request.method == 'POST':
        form = PaymentClaimSubmissionForm(
            request.POST, request.FILES,
            student_fee=student_fee,
            school=request.school
        )
        if form.is_valid():
            with transaction.atomic():
                submission = form.save(commit=False)
                submission.school = request.school
                submission.student_fee = student_fee
                submission.student = student_fee.student
                submission.submission_no = generate_claim_number(request.school)
                submission.submitted_by = request.user
                submission.status = 'PENDING_VERIFICATION'
                submission.save()

                FeeAuditLog.objects.create(
                    school=request.school,
                    user=request.user,
                    action='PAYMENT_CLAIM_SUBMITTED',
                    student=student_fee.student,
                    student_fee=student_fee,
                    submission=submission,
                    amount=submission.amount,
                    old_status=student_fee.status,
                    new_status='PENDING_VERIFICATION',
                    ip_address=get_client_ip(request),
                    details={
                        'submission_no': submission.submission_no,
                        'transaction_id': submission.transaction_id,
                        'payment_mode': submission.payment_mode,
                        'bank_name': submission.bank_name,
                        'has_proof_file': bool(submission.proof_file),
                    }
                )

            messages.success(
                request,
                f"Payment proof submitted successfully! Claim ID #{submission.submission_no}. "
                "School administration will verify the transaction and issue your official receipt."
            )
            return redirect('my_fees')
    else:
        # Pre-populate suggested amount with net due
        initial_data = {
            'amount': student_fee.net_due,
            'payment_date': date.today().isoformat(),
        }
        form = PaymentClaimSubmissionForm(
            initial=initial_data,
            student_fee=student_fee,
            school=request.school
        )

    return render(request, 'fees/submit_payment_claim.html', {
        'student_fee': student_fee,
        'form': form,
        'previous_arrears': previous_arrears,
        'past_unpaid_items': past_unpaid_items,
        'total_payable': total_payable,
    })


@login_required
def cancel_payment_claim_view(request, submission_id):
    """Student / Parent cancels their own pending claim prior to admin review."""
    submission = get_object_or_404(
        PaymentSubmission.objects.select_related('student', 'student_fee'),
        pk=submission_id,
        school=request.school
    )

    if not user_can_access_student(request.user, submission.student):
        return HttpResponseForbidden("Unauthorized to cancel this claim.")

    if submission.status != 'PENDING_VERIFICATION':
        messages.error(request, "Only pending verification claims can be cancelled.")
        return redirect('my_fees')

    if request.method == 'POST':
        with transaction.atomic():
            submission.status = 'CANCELLED'
            submission.save()

            FeeAuditLog.objects.create(
                school=request.school,
                user=request.user,
                action='PAYMENT_CLAIM_CANCELLED',
                student=submission.student,
                student_fee=submission.student_fee,
                submission=submission,
                amount=submission.amount,
                old_status='PENDING_VERIFICATION',
                new_status='CANCELLED',
                ip_address=get_client_ip(request),
                details={'submission_no': submission.submission_no}
            )

        messages.info(request, f"Payment claim #{submission.submission_no} has been cancelled.")
        return redirect('my_fees')

    return redirect('my_fees')


# ==========================================
# 4. ADMIN PAYMENT VERIFICATION PANEL
# ==========================================

@login_required
def fee_verifications_view(request):
    """Admin / Principal / Accountant Payment Verification Panel."""
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted to administrators and fee managers.")
        return redirect('dashboard')

    status_filter = request.GET.get('status', 'PENDING_VERIFICATION')
    class_filter = request.GET.get('class_id', '')
    query = request.GET.get('q', '').strip()

    claims = PaymentSubmission.objects.filter(school=request.school).select_related(
        'student', 'student__current_class', 'student__current_section',
        'student_fee', 'student_fee__fee_head', 'submitted_by', 'verified_by'
    )

    if status_filter and status_filter != 'ALL':
        claims = claims.filter(status=status_filter)

    if class_filter:
        claims = claims.filter(student__current_class_id=class_filter)

    if query:
        claims = claims.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__admission_no__icontains=query) |
            Q(transaction_id__icontains=query) |
            Q(submission_no__icontains=query)
        )

    # Pending count badge
    pending_count = PaymentSubmission.objects.filter(school=request.school, status='PENDING_VERIFICATION').count()
    classes = Class.objects.filter(school=request.school)

    approval_form = PaymentApprovalForm()
    rejection_form = PaymentRejectionForm()

    return render(request, 'fees/verifications.html', {
        'claims': claims,
        'status_filter': status_filter,
        'class_filter': class_filter,
        'query': query,
        'pending_count': pending_count,
        'classes': classes,
        'approval_form': approval_form,
        'rejection_form': rejection_form,
    })


@login_required
def approve_payment_claim_view(request, submission_id):
    """
    Admin verifies and approves student payment claim.
    Executes atomic database transaction:
    PaymentSubmission (VERIFIED) -> FeePayment (Created) -> StudentFee (Ledger Updated) -> FeeReceipt -> FeeAuditLog
    """
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        return HttpResponseForbidden("Access restricted.")

    if request.method != 'POST':
        return redirect('fee_verifications')

    form = PaymentApprovalForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please verify all approval form fields and check the confirmation box.")
        return redirect('fee_verifications')

    with transaction.atomic():
        try:
            submission = PaymentSubmission.objects.select_for_update().get(
                pk=submission_id, school=request.school
            )
        except PaymentSubmission.DoesNotExist:
            raise Http404("Payment claim not found.")

        if submission.status != 'PENDING_VERIFICATION':
            messages.error(request, f"This claim #{submission.submission_no} has already been {submission.get_status_display()}. Concurrency prevented duplicate verification.")
            return redirect('fee_verifications')

        student_fee = StudentFee.objects.select_for_update().get(
            pk=submission.student_fee_id, school=request.school
        )

        verified_amount = form.cleaned_data['verified_amount']
        payment_mode = form.cleaned_data['payment_mode']
        admin_notes = form.cleaned_data['admin_notes']

        if verified_amount <= 0:
            messages.error(request, "Verified payment amount must be greater than zero.")
            return redirect('fee_verifications')

        if verified_amount > student_fee.net_due:
            messages.error(
                request,
                f"Verified amount (₹{verified_amount:.2f}) exceeds current net due (₹{student_fee.net_due:.2f})."
            )
            return redirect('fee_verifications')

        # 1. Create Official FeePayment Ledger Record
        receipt_no = generate_receipt_number(request.school)
        payment = FeePayment.objects.create(
            school=request.school,
            student_fee=student_fee,
            submission=submission,
            receipt_no=receipt_no,
            amount_paid=verified_amount,
            payment_date=timezone.now(),
            payment_mode=payment_mode,
            transaction_id=submission.transaction_id,
            remarks=f"Verified online claim {submission.submission_no}. {admin_notes}".strip(),
            collected_by=request.user,
            status='VERIFIED'
        )

        # 2. Update PaymentSubmission
        submission.status = 'VERIFIED'
        submission.amount = verified_amount
        submission.admin_notes = admin_notes
        submission.verified_by = request.user
        submission.verified_at = timezone.now()
        submission.save()

        # 3. Create Immutable Audit Log
        FeeAuditLog.objects.create(
            school=request.school,
            user=request.user,
            action='PAYMENT_APPROVED',
            student=student_fee.student,
            student_fee=student_fee,
            payment=payment,
            submission=submission,
            amount=verified_amount,
            old_status='PENDING_VERIFICATION',
            new_status='VERIFIED',
            ip_address=get_client_ip(request),
            details={
                'receipt_no': receipt_no,
                'submission_no': submission.submission_no,
                'transaction_id': submission.transaction_id,
                'payment_mode': payment_mode,
                'verified_by': request.user.username,
                'admin_notes': admin_notes,
            }
        )

    messages.success(
        request,
        f"Payment claim #{submission.submission_no} approved! Official Receipt #{receipt_no} generated."
    )
    return redirect('fee_receipt', receipt_id=payment.pk)


@login_required
def reject_payment_claim_view(request, submission_id):
    """Admin rejects payment claim with mandatory reason."""
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        return HttpResponseForbidden("Access restricted.")

    if request.method != 'POST':
        return redirect('fee_verifications')

    form = PaymentRejectionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Rejection reason is mandatory.")
        return redirect('fee_verifications')

    with transaction.atomic():
        try:
            submission = PaymentSubmission.objects.select_for_update().get(
                pk=submission_id, school=request.school
            )
        except PaymentSubmission.DoesNotExist:
            raise Http404("Payment claim not found.")

        if submission.status != 'PENDING_VERIFICATION':
            messages.error(request, f"This claim has already been {submission.get_status_display()}.")
            return redirect('fee_verifications')

        rejection_reason = form.cleaned_data['rejection_reason']
        submission.status = 'REJECTED'
        submission.rejection_reason = rejection_reason
        submission.verified_by = request.user
        submission.verified_at = timezone.now()
        submission.save()

        FeeAuditLog.objects.create(
            school=request.school,
            user=request.user,
            action='PAYMENT_REJECTED',
            student=submission.student,
            student_fee=submission.student_fee,
            submission=submission,
            amount=submission.amount,
            old_status='PENDING_VERIFICATION',
            new_status='REJECTED',
            ip_address=get_client_ip(request),
            details={
                'submission_no': submission.submission_no,
                'rejection_reason': rejection_reason,
                'rejected_by': request.user.username,
            }
        )

    messages.warning(request, f"Payment claim #{submission.submission_no} rejected.")
    return redirect('fee_verifications')


# ==========================================
# 5. SECURE PROOF FILE SERVING (OWASP SAFE)
# ==========================================

@login_required
def secure_proof_view(request, submission_id):
    """
    Secure File Response for payment proofs.
    Prevents unauthenticated or cross-student access to uploaded payment receipts/screenshots.
    """
    submission = get_object_or_404(
        PaymentSubmission.objects.select_related('student'),
        pk=submission_id,
        school=request.school
    )

    if not user_can_access_student(request.user, submission.student):
        return HttpResponseForbidden("You do not have authorization to view this payment proof.")

    if not submission.proof_file:
        raise Http404("Payment proof file not attached.")

    try:
        file_obj = submission.proof_file.open('rb')
    except (FileNotFoundError, ValueError, OSError):
        raise Http404("Payment proof file could not be read from storage.")

    response = FileResponse(file_obj)
    response['X-Content-Type-Options'] = 'nosniff'
    return response


# ==========================================
# 6. OFFICIAL ERP RECEIPT & PUBLIC QR VERIFY
# ==========================================

@login_required
def fee_receipt_view(request, receipt_id):
    """
    Official School ERP Fee Receipt View.
    Protected by strict multi-tenant and IDOR authorization.
    """
    payment = get_object_or_404(
        FeePayment.objects.select_related(
            'student_fee', 'student_fee__student', 'student_fee__student__current_class',
            'student_fee__student__current_section', 'student_fee__school',
            'student_fee__fee_head', 'student_fee__academic_session', 'collected_by',
            'submission'
        ),
        pk=receipt_id,
        school=request.school
    )

    if not user_can_access_student(request.user, payment.student_fee.student):
        return HttpResponseForbidden("You do not have permission to access this receipt.")

    # Generate full public verification URL for QR code
    verification_url = request.build_absolute_uri(f"/fees/receipt/verify/{payment.verification_token}/")

    return render(request, 'fees/fee_receipt.html', {
        'payment': payment,
        'verification_url': verification_url,
    })


def verify_receipt_public_view(request, token):
    """
    Public QR Verification Endpoint (OWASP Compliant).
    Does NOT leak private student PII (masks student name).
    Gracefully handles invalid or malformed tokens.
    """
    import uuid
    try:
        val_uuid = uuid.UUID(str(token).strip())
    except (ValueError, TypeError, AttributeError):
        return render(request, 'fees/receipt_verify_public.html', {
            'is_valid': False,
            'token': token,
        }, status=404)

    payment = FeePayment.all_objects.select_related(
        'student_fee__school', 'student_fee__student',
        'student_fee__student__current_class', 'student_fee__fee_head'
    ).filter(verification_token=val_uuid).first()

    if not payment:
        return render(request, 'fees/receipt_verify_public.html', {
            'is_valid': False,
            'token': token,
        }, status=404)

    masked_name = mask_student_name(payment.student_fee.student)

    return render(request, 'fees/receipt_verify_public.html', {
        'is_valid': True,
        'payment': payment,
        'masked_student_name': masked_name,
        'verification_time': timezone.now(),
    })


# ==========================================
# 7. FEE ADJUSTMENTS & CORRECTIONS
# ==========================================

@login_required
def fee_adjustments_view(request):
    """View all historical fee adjustments and concessions."""
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted.")
        return redirect('dashboard')

    adjustments = FeeAdjustment.objects.filter(school=request.school).select_related(
        'student_fee__student', 'student_fee__fee_head', 'approved_by'
    )

    return render(request, 'fees/fee_adjustments.html', {
        'adjustments': adjustments,
    })


@login_required
def create_adjustment_view(request, fee_id):
    """Create an official concession, fine, or balance correction on a StudentFee."""
    if not (request.user.is_school_admin() or request.user.is_super_admin()):
        messages.error(request, "Only School Admins and Principals can approve fee adjustments.")
        return redirect('fee_defaulters')

    student_fee = get_object_or_404(
        StudentFee.objects.select_related('student', 'fee_head'),
        pk=fee_id,
        school=request.school
    )

    if request.method == 'POST':
        form = FeeAdjustmentForm(request.POST, student_fee=student_fee)
        if form.is_valid():
            with transaction.atomic():
                adj = form.save(commit=False)
                adj.school = request.school
                adj.student_fee = student_fee
                adj.approved_by = request.user
                adj.save()

                # Apply adjustment to student fee balance
                if adj.adjustment_type in ['DISCOUNT', 'WAIVER']:
                    student_fee.amount_discount += adj.amount
                elif adj.adjustment_type == 'FINE':
                    student_fee.amount_due += adj.amount
                elif adj.adjustment_type == 'CORRECTION':
                    # Correction decreases due or adjusts balance
                    student_fee.amount_discount += adj.amount

                student_fee.save()

                FeeAuditLog.objects.create(
                    school=request.school,
                    user=request.user,
                    action='FEE_ADJUSTMENT',
                    student=student_fee.student,
                    student_fee=student_fee,
                    amount=adj.amount,
                    old_status=student_fee.status,
                    new_status=student_fee.status,
                    ip_address=get_client_ip(request),
                    details={
                        'adjustment_type': adj.adjustment_type,
                        'reason': adj.reason,
                        'approved_by': request.user.username,
                    }
                )

            messages.success(request, f"Fee adjustment of ₹{adj.amount} applied to {student_fee.student.first_name}'s {student_fee.fee_head.name}.")
            return redirect('fee_adjustments')
    else:
        form = FeeAdjustmentForm(student_fee=student_fee)

    return render(request, 'fees/create_adjustment.html', {
        'student_fee': student_fee,
        'form': form,
    })


# ==========================================
# 8. PAYMENT VOID / REVERSAL & REFUNDS
# ==========================================

@login_required
def reverse_payment_view(request, payment_id):
    """
    Void / Reverse an existing verified payment with mandatory reason.
    No hard deletes allowed!
    """
    if not (request.user.is_school_admin() or request.user.is_super_admin()):
        messages.error(request, "Only School Admins or Principals can reverse payments.")
        return redirect('fee_defaulters')

    payment = get_object_or_404(
        FeePayment.objects.select_related('student_fee', 'student_fee__student'),
        pk=payment_id,
        school=request.school
    )

    if payment.status != 'VERIFIED':
        messages.warning(request, f"This payment cannot be reversed because its status is {payment.get_status_display()}.")
        return redirect('fee_receipt', receipt_id=payment.pk)

    if request.method == 'POST':
        form = PaymentReversalForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                reason = form.cleaned_data['reversal_reason']
                payment.status = 'REVERSED'
                payment.reversal_reason = reason
                payment.reversed_by = request.user
                payment.reversed_at = timezone.now()
                payment.save()  # Triggers recalculate_fee_ledger() automatically

                FeeAuditLog.objects.create(
                    school=request.school,
                    user=request.user,
                    action='PAYMENT_REVERSED',
                    student=payment.student_fee.student,
                    student_fee=payment.student_fee,
                    payment=payment,
                    amount=payment.amount_paid,
                    old_status='VERIFIED',
                    new_status='REVERSED',
                    ip_address=get_client_ip(request),
                    details={
                        'receipt_no': payment.receipt_no,
                        'reversal_reason': reason,
                        'reversed_by': request.user.username,
                    }
                )

            messages.warning(request, f"Payment Receipt #{payment.receipt_no} has been reversed/voided.")
            return redirect('fee_defaulters')
    else:
        form = PaymentReversalForm()

    return render(request, 'fees/reverse_payment.html', {
        'payment': payment,
        'form': form,
    })


@login_required
def fee_refunds_view(request):
    """View all payment refunds and chargebacks."""
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted.")
        return redirect('dashboard')

    refunds = PaymentRefund.objects.filter(school=request.school).select_related(
        'payment', 'payment__student_fee__student', 'payment__student_fee__fee_head',
        'requested_by', 'approved_by'
    )

    return render(request, 'fees/fee_refunds.html', {
        'refunds': refunds,
    })


@login_required
def create_refund_request_view(request, payment_id):
    """Initiate a refund request on an active verified payment."""
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted.")
        return redirect('dashboard')

    payment = get_object_or_404(
        FeePayment.objects.select_related('student_fee', 'student_fee__student'),
        pk=payment_id,
        school=request.school,
        status='VERIFIED'
    )

    if request.method == 'POST':
        form = PaymentRefundForm(request.POST, payment=payment)
        if form.is_valid():
            with transaction.atomic():
                refund = form.save(commit=False)
                refund.school = request.school
                refund.payment = payment
                refund.refund_no = generate_refund_number(request.school)
                refund.requested_by = request.user
                refund.status = 'REQUESTED'
                refund.save()

                FeeAuditLog.objects.create(
                    school=request.school,
                    user=request.user,
                    action='REFUND_REQUESTED',
                    student=payment.student_fee.student,
                    student_fee=payment.student_fee,
                    payment=payment,
                    amount=refund.amount,
                    ip_address=get_client_ip(request),
                    details={
                        'refund_no': refund.refund_no,
                        'receipt_no': payment.receipt_no,
                        'reason': refund.reason,
                    }
                )

            messages.success(request, f"Refund request #{refund.refund_no} submitted for approval.")
            return redirect('fee_refunds')
    else:
        form = PaymentRefundForm(payment=payment, initial={'amount': payment.amount_paid})

    return render(request, 'fees/create_refund.html', {
        'payment': payment,
        'form': form,
    })


@login_required
def process_refund_view(request, refund_id):
    """Approve or Process a refund request."""
    if not (request.user.is_school_admin() or request.user.is_super_admin()):
        messages.error(request, "Only School Admins or Principals can process refunds.")
        return redirect('fee_refunds')

    refund = get_object_or_404(
        PaymentRefund.objects.select_related('payment', 'payment__student_fee'),
        pk=refund_id,
        school=request.school
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        with transaction.atomic():
            if action == 'APPROVE_PROCESS':
                refund.status = 'PROCESSED'
                refund.approved_by = request.user
                refund.processed_at = timezone.now()
                refund.transaction_ref = request.POST.get('transaction_ref', '')
                refund.save()

                payment = refund.payment
                from decimal import Decimal
                total_processed = payment.refunds.filter(status='PROCESSED').aggregate(tot=Sum('amount'))['tot'] or Decimal('0.00')
                if total_processed >= payment.amount_paid:
                    payment.status = 'REFUNDED'
                    payment.save()
                else:
                    payment.recalculate_fee_ledger()

                FeeAuditLog.objects.create(
                    school=request.school,
                    user=request.user,
                    action='REFUND_PROCESSED',
                    student=payment.student_fee.student,
                    student_fee=payment.student_fee,
                    payment=payment,
                    amount=refund.amount,
                    old_status='REQUESTED',
                    new_status='PROCESSED',
                    ip_address=get_client_ip(request),
                    details={
                        'refund_no': refund.refund_no,
                        'receipt_no': payment.receipt_no,
                        'transaction_ref': refund.transaction_ref,
                    }
                )
                messages.success(request, f"Refund #{refund.refund_no} has been processed and ledger updated.")
            elif action == 'REJECT':
                refund.status = 'REJECTED'
                refund.approved_by = request.user
                refund.processed_at = timezone.now()
                refund.save()

                FeeAuditLog.objects.create(
                    school=request.school,
                    user=request.user,
                    action='REFUND_REJECTED',
                    student=refund.payment.student_fee.student,
                    student_fee=refund.payment.student_fee,
                    payment=refund.payment,
                    amount=refund.amount,
                    old_status='REQUESTED',
                    new_status='REJECTED',
                    ip_address=get_client_ip(request),
                    details={'refund_no': refund.refund_no}
                )
                messages.warning(request, f"Refund #{refund.refund_no} was rejected.")

        return redirect('fee_refunds')

    return redirect('fee_refunds')


# ==========================================
# 9. DAILY FEE CLOSING & RECONCILIATION
# ==========================================

@login_required
def daily_closing_view(request):
    """Daily Fee Closing Register."""
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted.")
        return redirect('dashboard')

    date_str = request.GET.get('date', date.today().isoformat())
    try:
        closing_dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        closing_dt = date.today()

    from decimal import Decimal
    payments_today = FeePayment.objects.filter(
        school=request.school,
        payment_date__date=closing_dt,
        status='VERIFIED'
    )

    cash_tot = payments_today.filter(payment_mode='CASH').aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')
    upi_tot = payments_today.filter(payment_mode='UPI').aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')
    bank_tot = payments_today.filter(payment_mode='BANK_TRANSFER').aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')
    cheque_tot = payments_today.filter(payment_mode='CHEQUE').aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')
    online_tot = payments_today.filter(payment_mode__in=['ONLINE', 'CARD']).aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')
    other_tot = payments_today.filter(payment_mode='OTHER').aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')

    total_collected = cash_tot + upi_tot + bank_tot + cheque_tot + online_tot + other_tot

    refunds_today = PaymentRefund.objects.filter(
        school=request.school,
        processed_at__date=closing_dt,
        status='PROCESSED'
    ).aggregate(tot=Sum('amount'))['tot'] or Decimal('0.00')

    net_closing = total_collected - refunds_today

    existing_closing = DailyFeeClosing.objects.filter(school=request.school, closing_date=closing_dt).first()

    if request.method == 'POST':
        notes = request.POST.get('notes', '').strip()
        closing, _ = DailyFeeClosing.objects.update_or_create(
            school=request.school,
            closing_date=closing_dt,
            defaults={
                'cash_total': cash_tot,
                'upi_total': upi_tot,
                'bank_total': bank_tot,
                'cheque_total': cheque_tot,
                'online_total': online_tot,
                'other_total': other_tot,
                'total_collected': total_collected,
                'total_refunded': refunds_today,
                'net_closing': net_closing,
                'closed_by': request.user,
                'notes': notes,
            }
        )

        FeeAuditLog.objects.create(
            school=request.school,
            user=request.user,
            action='DAILY_CLOSING_SUBMITTED',
            amount=net_closing,
            ip_address=get_client_ip(request),
            details={
                'date': str(closing_dt),
                'total_collected': str(total_collected),
                'total_refunded': str(refunds_today),
                'net_closing': str(net_closing),
            }
        )

        messages.success(request, f"Daily Fee Closing for {closing_dt.strftime('%d %b %Y')} submitted successfully!")
        return redirect(f"{request.path}?date={closing_dt.isoformat()}")

    # Past closings
    past_closings = DailyFeeClosing.objects.filter(school=request.school).order_by('-closing_date')[:15]

    return render(request, 'fees/daily_closing.html', {
        'closing_dt': closing_dt,
        'cash_tot': cash_tot,
        'upi_tot': upi_tot,
        'bank_tot': bank_tot,
        'cheque_tot': cheque_tot,
        'online_tot': online_tot,
        'other_tot': other_tot,
        'total_collected': total_collected,
        'refunds_today': refunds_today,
        'net_closing': net_closing,
        'existing_closing': existing_closing,
        'payments_today': payments_today,
        'past_closings': past_closings,
    })


@login_required
def fee_reconciliation_view(request):
    """Financial Reconciliation & Comprehensive Audit Analytics for Admin & Principal."""
    if not (request.user.can_manage_fees() or request.user.is_super_admin()):
        messages.error(request, "Access restricted.")
        return redirect('dashboard')

    from decimal import Decimal
    # Total Assigned Dues
    total_assigned = StudentFee.objects.filter(school=request.school).aggregate(tot=Sum('amount_due'))['tot'] or Decimal('0.00')
    total_discounts = StudentFee.objects.filter(school=request.school).aggregate(tot=Sum('amount_discount'))['tot'] or Decimal('0.00')
    total_collected = FeePayment.objects.filter(school=request.school, status='VERIFIED').aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')
    total_refunded = PaymentRefund.objects.filter(school=request.school, status='PROCESSED').aggregate(tot=Sum('amount'))['tot'] or Decimal('0.00')
    
    under_verification_tot = PaymentSubmission.objects.filter(
        school=request.school, status='PENDING_VERIFICATION'
    ).aggregate(tot=Sum('amount'))['tot'] or Decimal('0.00')

    pending_qs = StudentFee.objects.filter(school=request.school)
    total_outstanding = sum([f.net_due for f in pending_qs], Decimal('0.00'))

    # Category Head Breakdown
    fee_heads = FeeHead.objects.filter(school=request.school)
    head_stats = []
    for h in fee_heads:
        fees_h = StudentFee.objects.filter(school=request.school, fee_head=h)
        h_assigned = fees_h.aggregate(tot=Sum('amount_due'))['tot'] or Decimal('0.00')
        h_paid = fees_h.aggregate(tot=Sum('amount_paid'))['tot'] or Decimal('0.00')
        h_due = sum([f.net_due for f in fees_h], Decimal('0.00'))
        head_stats.append({
            'head': h,
            'assigned': h_assigned,
            'paid': h_paid,
            'outstanding': h_due,
        })

    # Mode breakdown
    mode_counts = FeePayment.objects.filter(school=request.school, status='VERIFIED').values('payment_mode').annotate(
        total_amount=Sum('amount_paid'),
        count=Count('id')
    )

    return render(request, 'fees/reconciliation.html', {
        'total_assigned': total_assigned,
        'total_discounts': total_discounts,
        'total_collected': total_collected,
        'total_refunded': total_refunded,
        'net_revenue': total_collected - total_refunded,
        'total_outstanding': total_outstanding,
        'under_verification_tot': under_verification_tot,
        'head_stats': head_stats,
        'mode_counts': mode_counts,
    })


# ==========================================
# 10. IMMUTABLE FINANCIAL AUDIT LOGS
# ==========================================

@login_required
def fee_audit_logs_view(request):
    """View Immutable Audit Trail (OWASP Financial Compliance)."""
    if not (request.user.is_school_admin() or request.user.is_super_admin()):
        messages.error(request, "Access restricted to School Administrators and Principals.")
        return redirect('dashboard')

    action_filter = request.GET.get('action', '')
    logs = FeeAuditLog.objects.filter(school=request.school).select_related('user', 'student')

    if action_filter:
        logs = logs.filter(action=action_filter)

    logs = logs[:100]

    return render(request, 'fees/fee_audit_logs.html', {
        'logs': logs,
        'action_filter': action_filter,
    })
