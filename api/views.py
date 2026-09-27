import uuid
from decimal import Decimal
from datetime import date
from django.db import models
from django.db.models import Q, Sum
from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from accounts.models import User, set_current_school
from schools.models import School, AcademicSession, Notice
from academics.models import Class, Section, Subject, Timetable
from students.models import Student
from teachers.models import Teacher
from attendance.models import StudentAttendance
from fees.models import StudentFee, PaymentSubmission, FeeHead
from examinations.models import Exam, MarksEntry
from homework.models import Homework, StudyMaterial

from api.serializers import (
    UserSerializer, SchoolSerializer, StudentProfileSerializer, TeacherProfileSerializer,
    ClassSerializer, SectionSerializer, SubjectSerializer, TimetableSerializer,
    StudentFeeSerializer, PaymentSubmissionSerializer, StudentAttendanceSerializer,
    HomeworkSerializer, StudyMaterialSerializer, NoticeSerializer, MarksEntrySerializer
)


class LoginAPIView(APIView):
    """
    Mobile / Web Login API.
    Accepts: { 'username': '...', 'password': '...', 'school_code': 'optional' }
    Returns: Token, User, School, Student/Teacher Profile.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        school_code = request.data.get('school_code', '').strip()

        if not username or not password:
            return Response(
                {'error': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Your user account has been disabled.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # School verification (if school_code is supplied)
        school = user.school
        if school_code:
            if not school or school.code.lower() != school_code.lower():
                return Response(
                    {'error': f"User account does not belong to school code '{school_code}'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not school and not user.is_superuser:
            school = School.objects.filter(is_active=True).first()

        # Set tenant context
        if school:
            set_current_school(school)

        token, _ = Token.objects.get_or_create(user=user)

        user_data = UserSerializer(user).data
        school_data = SchoolSerializer(school).data if school else None

        student_data = None
        teacher_data = None

        if hasattr(user, 'student_profile') and user.student_profile:
            student_data = StudentProfileSerializer(user.student_profile).data
        elif hasattr(user, 'teacher_profile') and user.teacher_profile:
            teacher_data = TeacherProfileSerializer(user.teacher_profile).data

        return Response({
            'token': token.key,
            'user': user_data,
            'school': school_data,
            'student_profile': student_data,
            'teacher_profile': teacher_data,
        }, status=status.HTTP_200_OK)


class UserProfileAPIView(APIView):
    """
    Returns current authenticated user profile & associated school details.
    """
    def get(self, request):
        user = request.user
        student_data = StudentProfileSerializer(user.student_profile).data if hasattr(user, 'student_profile') and user.student_profile else None
        teacher_data = TeacherProfileSerializer(user.teacher_profile).data if hasattr(user, 'teacher_profile') and user.teacher_profile else None

        return Response({
            'user': UserSerializer(user).data,
            'school': SchoolSerializer(request.school).data if getattr(request, 'school', None) else None,
            'student_profile': student_data,
            'teacher_profile': teacher_data,
        })


class StudentDashboardAPIView(APIView):
    """
    Comprehensive student dashboard data:
    - Student Profile Details
    - Attendance Percentage & Summary
    - Fee Dues, Paid, Arrears, Under Review
    - Active Homeworks count & list
    - Recent School Notices
    - Today's Class Routine Preview
    """
    def get(self, request):
        user = request.user
        student = getattr(user, 'student_profile', None)

        # Allow parents to inspect their first child or specified child_id
        if user.is_parent_user():
            child_id = request.GET.get('student_id')
            if child_id:
                student = user.children.filter(pk=child_id).first()
            else:
                student = user.children.first()

        if not student:
            return Response({'error': 'No student profile linked to this user.'}, status=status.HTTP_404_NOT_FOUND)

        # 1. Attendance Analytics
        attendances = student.attendances.all()
        tot_att = attendances.count()
        pres_att = attendances.filter(status='P').count()
        att_pct = round((pres_att / tot_att) * 100, 1) if tot_att > 0 else 100.0

        # 2. Fee Financials
        today_dt = date.today()
        fees_qs = student.fees.select_related('fee_head', 'academic_session').prefetch_related('submissions').all()
        total_invoiced = sum([f.amount_due for f in fees_qs], Decimal('0.00'))
        total_paid = sum([f.amount_paid for f in fees_qs], Decimal('0.00'))
        total_due = sum([f.net_due for f in fees_qs], Decimal('0.00'))
        total_under_review = sum([f.under_review_amount for f in fees_qs], Decimal('0.00'))
        past_arrears = sum([f.net_due for f in fees_qs if f.due_date and f.due_date < today_dt], Decimal('0.00'))

        # 3. Homework & Notices
        homeworks = Homework.objects.filter(
            class_level=student.current_class, section=student.current_section
        ).order_by('-assigned_date')[:5]

        notices = Notice.objects.filter(
            school=request.school, is_active=True
        ).filter(Q(target_role='ALL') | Q(target_role='STUDENT')).order_by('-created_at')[:5]

        # 4. Today's Routine
        today_day_name = date.today().strftime('%A')
        today_schedule = Timetable.objects.filter(
            class_level=student.current_class, section=student.current_section, day=today_day_name
        ).select_related('subject', 'teacher_user').order_by('period_number')

        return Response({
            'student': StudentProfileSerializer(student).data,
            'attendance': {
                'percentage': att_pct,
                'total_days': tot_att,
                'present_days': pres_att,
                'absent_days': attendances.filter(status='A').count(),
                'leave_days': attendances.filter(status__in=['L', 'LE', 'H']).count(),
            },
            'fees': {
                'total_invoiced': float(total_invoiced),
                'total_paid': float(total_paid),
                'total_due': float(total_due),
                'total_under_review': float(total_under_review),
                'past_arrears': float(past_arrears),
                'pending_fee_items_count': fees_qs.filter(status__in=['PENDING', 'PARTIAL', 'OVERDUE']).count(),
            },
            'homeworks': HomeworkSerializer(homeworks, many=True).data,
            'notices': NoticeSerializer(notices, many=True).data,
            'today_schedule': TimetableSerializer(today_schedule, many=True).data,
            'today_day': today_day_name,
        })


class TimetableAPIView(APIView):
    """
    Returns Structured Weekly Routine Grid Matrix:
    - Days: Monday to Saturday
    - Morning Periods (1st to 4th)
    - Vertical Break separator info
    - Afternoon Periods (5th to 8th + Extra Class)
    - Subject Name + Teacher Name in bracket: MATHS (Abhi Singh)
    """
    def get(self, request):
        user = request.user
        class_id = request.GET.get('class_id')
        section_id = request.GET.get('section_id')

        # Auto-resolve class & section if not provided
        if hasattr(user, 'student_profile') and user.student_profile:
            if not class_id:
                class_id = user.student_profile.current_class_id
            if not section_id:
                section_id = user.student_profile.current_section_id
        elif user.is_parent_user():
            child = user.children.first()
            if child:
                if not class_id:
                    class_id = child.current_class_id
                if not section_id:
                    section_id = child.current_section_id

        if not class_id:
            first_cls = Class.objects.filter(school=request.school).first()
            if first_cls:
                class_id = first_cls.id
                first_sec = Section.objects.filter(school=request.school, class_level=first_cls).first()
                if first_sec:
                    section_id = first_sec.id

        timetables_qs = Timetable.objects.filter(
            school=request.school
        ).select_related('class_level', 'section', 'subject', 'teacher_user')

        if class_id:
            timetables_qs = timetables_qs.filter(class_level_id=class_id)
        if section_id:
            timetables_qs = timetables_qs.filter(section_id=section_id)

        selected_class_obj = Class.objects.filter(id=class_id).first() if class_id else None
        selected_section_obj = Section.objects.filter(id=section_id).first() if section_id else None

        DAYS_LIST = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        MORNING_PERIODS = [1, 2, 3, 4]
        AFTERNOON_PERIODS = [5, 6, 7, 8, 9]

        tt_map = {}
        for tt in timetables_qs:
            tt_map[(tt.day, tt.period_number)] = TimetableSerializer(tt).data

        grid_rows = []
        for day in DAYS_LIST:
            morning_cells = []
            for p in MORNING_PERIODS:
                morning_cells.append({
                    'period_number': p,
                    'item': tt_map.get((day, p)),
                })

            afternoon_cells = []
            for p in AFTERNOON_PERIODS:
                afternoon_cells.append({
                    'period_number': p,
                    'item': tt_map.get((day, p)),
                })

            grid_rows.append({
                'day': day,
                'day_display': day.upper(),
                'morning': morning_cells,
                'afternoon': afternoon_cells,
            })

        return Response({
            'selected_class': ClassSerializer(selected_class_obj).data if selected_class_obj else None,
            'selected_section': SectionSerializer(selected_section_obj).data if selected_section_obj else None,
            'grid_rows': grid_rows,
            'all_entries': TimetableSerializer(timetables_qs, many=True).data,
        })


class FeeListAPIView(APIView):
    """
    List all fees for current student with financial summary, breakdown, and arrears.
    """
    def get(self, request):
        user = request.user
        student = getattr(user, 'student_profile', None)

        if user.is_parent_user():
            student = user.children.first()

        if not student:
            return Response({'error': 'No student profile found.'}, status=status.HTTP_404_NOT_FOUND)

        fees = student.fees.select_related('fee_head', 'academic_session').prefetch_related('submissions').all()
        today_dt = date.today()

        total_invoiced = sum([f.amount_due for f in fees], Decimal('0.00'))
        total_paid = sum([f.amount_paid for f in fees], Decimal('0.00'))
        total_due = sum([f.net_due for f in fees], Decimal('0.00'))
        total_under_review = sum([f.under_review_amount for f in fees], Decimal('0.00'))
        past_arrears = sum([f.net_due for f in fees if f.due_date and f.due_date < today_dt], Decimal('0.00'))

        return Response({
            'summary': {
                'total_invoiced': float(total_invoiced),
                'total_paid': float(total_paid),
                'total_due': float(total_due),
                'total_under_review': float(total_under_review),
                'past_arrears': float(past_arrears),
            },
            'fees': StudentFeeSerializer(fees, many=True).data,
        })


class PaymentSubmissionAPIView(APIView):
    """
    Submit and list online payment slips / proofs.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user = request.user
        student = getattr(user, 'student_profile', None)
        if user.is_parent_user():
            student = user.children.first()

        if not student:
            return Response({'error': 'No student profile found.'}, status=status.HTTP_404_NOT_FOUND)

        submissions = PaymentSubmission.objects.filter(
            school=request.school, student=student
        ).select_related('student_fee__fee_head').order_by('-submitted_at')

        return Response(PaymentSubmissionSerializer(submissions, many=True).data)

    def post(self, request):
        user = request.user
        student = getattr(user, 'student_profile', None)
        if user.is_parent_user():
            student = user.children.first()

        if not student:
            return Response({'error': 'No student profile found.'}, status=status.HTTP_404_NOT_FOUND)

        fee_id = request.data.get('student_fee_id')
        if not fee_id:
            return Response({'error': 'student_fee_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        fee = StudentFee.objects.filter(school=request.school, student=student, pk=fee_id).first()
        if not fee:
            return Response({'error': 'Fee record not found for this student.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            amount = Decimal(str(request.data.get('amount', '0.00')))
        except Exception:
            return Response({'error': 'Invalid amount value.'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= Decimal('0.00'):
            return Response({'error': 'Payment amount must be greater than ₹0.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Amount cannot exceed net due amount
        if amount > fee.net_due:
            return Response({
                'error': f"Amount ₹{amount} exceeds remaining net due ₹{fee.net_due:.2f}. Overpayment is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check existing pending submission
        if fee.has_pending_submission:
            return Response({
                'error': 'A payment submission for this fee is already under review by school administration.'
            }, status=status.HTTP_400_BAD_REQUEST)

        transaction_id = request.data.get('transaction_id', '').strip()
        if not transaction_id:
            return Response({'error': 'Transaction / UTR ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        payment_mode = request.data.get('payment_mode', 'UPI')
        bank_name = request.data.get('bank_name', '')
        student_note = request.data.get('student_note', '')
        proof_file = request.FILES.get('proof_file')

        submission_no = f"CLM-{date.today().year}-{uuid.uuid4().hex[:8].upper()}"

        submission = PaymentSubmission.objects.create(
            school=request.school,
            student_fee=fee,
            student=student,
            submission_no=submission_no,
            amount=amount,
            payment_date=date.today(),
            payment_mode=payment_mode,
            transaction_id=transaction_id,
            bank_name=bank_name,
            proof_file=proof_file,
            student_note=student_note,
            submitted_by=user,
            status='PENDING_VERIFICATION'
        )

        return Response({
            'message': 'Payment proof submitted successfully and is now under review by school administration.',
            'submission': PaymentSubmissionSerializer(submission).data,
        }, status=status.HTTP_201_CREATED)


class AttendanceAPIView(APIView):
    """
    Student attendance history and monthly summary.
    """
    def get(self, request):
        user = request.user
        student = getattr(user, 'student_profile', None)
        if user.is_parent_user():
            student = user.children.first()

        if not student:
            return Response({'error': 'No student profile found.'}, status=status.HTTP_404_NOT_FOUND)

        attendances = student.attendances.select_related('class_level', 'section').order_by('-date')
        tot = attendances.count()
        pres = attendances.filter(status='P').count()
        pct = round((pres / tot) * 100, 1) if tot > 0 else 100.0

        return Response({
            'percentage': pct,
            'total_days': tot,
            'present_days': pres,
            'absent_days': attendances.filter(status='A').count(),
            'leave_days': attendances.filter(status__in=['L', 'LE', 'H']).count(),
            'history': StudentAttendanceSerializer(attendances[:60], many=True).data,
        })


class HomeworkAPIView(APIView):
    """
    Homework list and creation.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user = request.user
        if hasattr(user, 'student_profile') and user.student_profile:
            student = user.student_profile
            homeworks = Homework.objects.filter(
                class_level=student.current_class, section=student.current_section
            ).select_related('class_level', 'section', 'subject', 'created_by').order_by('-assigned_date')
        elif hasattr(user, 'teacher_profile') and user.teacher_profile:
            homeworks = Homework.objects.filter(
                created_by=user
            ).select_related('class_level', 'section', 'subject', 'created_by').order_by('-assigned_date')
        else:
            homeworks = Homework.objects.filter(
                school=request.school
            ).select_related('class_level', 'section', 'subject', 'created_by').order_by('-assigned_date')

        return Response(HomeworkSerializer(homeworks, many=True).data)

    def post(self, request):
        user = request.user
        if not user.is_teacher_user() and not user.is_school_admin():
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        class_id = request.data.get('class_level')
        section_id = request.data.get('section')
        subject_id = request.data.get('subject')
        title = request.data.get('title', '').strip()
        description = request.data.get('description', '').strip()
        due_date = request.data.get('due_date')
        attachment = request.FILES.get('attachment')

        if not all([class_id, section_id, subject_id, title, due_date]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        hw = Homework.objects.create(
            school=request.school,
            class_level_id=class_id,
            section_id=section_id,
            subject_id=subject_id,
            title=title,
            description=description,
            due_date=due_date,
            attachment=attachment,
            created_by=user
        )

        return Response(HomeworkSerializer(hw).data, status=status.HTTP_201_CREATED)


class StudyMaterialAPIView(APIView):
    """
    Study notes and materials list.
    """
    def get(self, request):
        user = request.user
        materials = StudyMaterial.objects.filter(school=request.school).select_related('class_level', 'subject', 'uploaded_by')

        if hasattr(user, 'student_profile') and user.student_profile:
            materials = materials.filter(class_level=user.student_profile.current_class)

        return Response(StudyMaterialSerializer(materials.order_by('-uploaded_at'), many=True).data)


class NoticeAPIView(APIView):
    """
    Announcements & Notices.
    """
    def get(self, request):
        user = request.user
        role = 'ALL'
        if hasattr(user, 'student_profile') and user.student_profile:
            role = 'STUDENT'
        elif hasattr(user, 'teacher_profile') and user.teacher_profile:
            role = 'TEACHER'
        elif user.is_parent_user():
            role = 'PARENT'

        notices = Notice.objects.filter(
            school=request.school, is_active=True
        ).filter(Q(target_role='ALL') | Q(target_role=role)).order_by('-created_at')

        return Response(NoticeSerializer(notices, many=True).data)


class ReportCardAPIView(APIView):
    """
    Student exam marks and report card summary.
    """
    def get(self, request):
        user = request.user
        student = getattr(user, 'student_profile', None)
        if user.is_parent_user():
            student = user.children.first()

        if not student:
            return Response({'error': 'No student profile found.'}, status=status.HTTP_404_NOT_FOUND)

        exam_id = request.GET.get('exam_id')
        marks = student.marks.select_related('exam', 'subject').order_by('subject__name')
        if exam_id:
            marks = marks.filter(exam_id=exam_id)

        tot_obtained = sum([m.total_marks_obtained for m in marks], Decimal('0.00'))
        tot_max = sum([m.subject.max_marks for m in marks], Decimal('0.00'))
        pct = round((float(tot_obtained) / float(tot_max)) * 100.0, 1) if tot_max > 0 else 0.0

        return Response({
            'student': StudentProfileSerializer(student).data,
            'percentage': pct,
            'total_obtained': float(tot_obtained),
            'total_max': float(tot_max),
            'marks': MarksEntrySerializer(marks, many=True).data,
        })
