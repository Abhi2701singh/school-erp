import uuid
from django.utils import timezone
from accounts.models import User


def get_client_ip(request):
    """
    Safely extract real client IP address handling Cloudflare and reverse proxies.
    """
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip.strip()

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        return ip

    return request.META.get('REMOTE_ADDR')


def generate_receipt_number(school):
    """
    Generate sequential, tamper-proof official fee receipt number.
    Format: REC-YYYY-XXXXXX (e.g. REC-2026-000001)
    """
    from fees.models import FeePayment
    year = timezone.now().year
    school_id = school.id if hasattr(school, 'id') else school
    prefix = f"REC-{year}-"
    
    count = FeePayment.all_objects.filter(school_id=school_id, payment_date__year=year).count() + 1
    receipt_no = f"{prefix}{count:06d}"
    
    while FeePayment.all_objects.filter(receipt_no=receipt_no).exists():
        count += 1
        receipt_no = f"{prefix}{count:06d}"
        
    return receipt_no


def generate_claim_number(school):
    """
    Generate sequential claim number for student payment proofs.
    Format: CLM-YYYY-XXXXXX (e.g. CLM-2026-000001)
    """
    from fees.models import PaymentSubmission
    year = timezone.now().year
    school_id = school.id if hasattr(school, 'id') else school
    prefix = f"CLM-{year}-"
    
    count = PaymentSubmission.all_objects.filter(school_id=school_id, submitted_at__year=year).count() + 1
    claim_no = f"{prefix}{count:06d}"
    
    while PaymentSubmission.all_objects.filter(submission_no=claim_no).exists():
        count += 1
        claim_no = f"{prefix}{count:06d}"
        
    return claim_no


def generate_refund_number(school):
    """
    Generate sequential refund reference number.
    Format: REF-YYYY-XXXXXX (e.g. REF-2026-000001)
    """
    from fees.models import PaymentRefund
    year = timezone.now().year
    school_id = school.id if hasattr(school, 'id') else school
    prefix = f"REF-{year}-"
    
    count = PaymentRefund.all_objects.filter(school_id=school_id, requested_at__year=year).count() + 1
    ref_no = f"{prefix}{count:06d}"
    
    while PaymentRefund.all_objects.filter(refund_no=ref_no).exists():
        count += 1
        ref_no = f"{prefix}{count:06d}"
        
    return ref_no


def user_can_access_student(user, student):
    """
    Check if the authenticated user has legitimate authorization to access the student's fee data.
    Prevents IDOR and cross-student data leakage.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_super_admin():
        return True

    # Check school isolation
    if user.school_id and student.school_id and user.school_id != student.school_id:
        return False

    # Staff / Admin / Principal / Accountant
    if user.can_manage_fees():
        return True

    # Student self-access
    if user.is_student_user():
        student_prof = getattr(user, 'student_profile', None)
        return bool(student_prof and student_prof.pk == student.pk)

    # Parent access
    if user.is_parent_user():
        parent_prof = getattr(user, 'parent_profile', None)
        return bool(parent_prof and parent_prof.students.filter(pk=student.pk).exists())

    return False


def mask_student_name(student):
    """
    Mask student name for public QR verification view to prevent PII leakage (OWASP).
    e.g. "Rahul Kumar" -> "Rahul K."
    """
    first = student.first_name.strip()
    last = student.last_name.strip() if student.last_name else ''
    if last:
        return f"{first} {last[0]}."
    return first
