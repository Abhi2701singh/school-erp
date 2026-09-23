import json
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from accounts.models import User
from schools.models import School, Notice, AcademicSession
from students.models import Student, ParentProfile
from teachers.models import Teacher
from academics.models import Class, Section, Timetable
from attendance.models import StudentAttendance
from examinations.models import Exam, MarksEntry
from fees.models import StudentFee, FeePayment
from homework.models import Homework, StudyMaterial

@login_required
def dashboard_router_view(request):
    user = request.user

    # Super Admin Dashboard
    if user.is_super_admin():
        total_schools = School.objects.count()
        active_schools = School.objects.filter(is_active=True).count()
        total_students_all = Student.all_objects.count()
        total_teachers_all = Teacher.all_objects.count()
        schools = School.objects.all()
        for s in schools:
            s.admin_user = User.objects.filter(school=s, role__in=[User.Roles.SCHOOL_ADMIN, User.Roles.PRINCIPAL]).first()

        return render(request, 'dashboard/super_admin.html', {
            'total_schools': total_schools,
            'active_schools': active_schools,
            'total_students_all': total_students_all,
            'total_teachers_all': total_teachers_all,
            'schools': schools,
        })

    # School Admin / Principal Dashboard
    if user.is_school_admin():
        active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()

        db_students_count = Student.objects.filter(school=request.school, status='ACTIVE').count()
        db_teachers_count = Teacher.objects.filter(school=request.school).count()
        db_classes_count = Class.objects.filter(school=request.school).count()

        today_dt = date.today()
        today_formatted = today_dt.strftime("%a, %d %b %Y")
        today_atts = StudentAttendance.objects.filter(school=request.school, date=today_dt)
        today_present = today_atts.filter(status='P').count()
        today_absent = today_atts.filter(status='A').count()
        today_leave = today_atts.filter(status__in=['L', 'LE']).count()
        today_total = today_atts.count()
        attendance_pct = round((today_present / today_total) * 100, 1) if today_total > 0 else 0.0

        # Fee Analytics
        from fees.models import PaymentSubmission
        fee_collected_total = FeePayment.objects.filter(school=request.school, status='VERIFIED').aggregate(total=Sum('amount_paid'))['total'] or 0.0
        pending_verifications_count = PaymentSubmission.objects.filter(school=request.school, status='PENDING_VERIFICATION').count()
        pending_fees = StudentFee.objects.filter(school=request.school, status__in=['PENDING', 'PARTIAL', 'OVERDUE'])
        defaulters_count = pending_fees.values('student').distinct().count()

        # Real Metric Counters from Database
        total_students_display = db_students_count
        total_teachers_display = db_teachers_count
        fee_collected_display = f"{int(fee_collected_total):,}"
        defaulters_count_display = defaulters_count

        # Real Recent Admissions from Database
        db_recent_students = list(Student.objects.filter(school=request.school).select_related('current_class', 'current_section').order_by('-created_at')[:5])
        recent_admissions = []
        for s in db_recent_students:
            recent_admissions.append({
                'name': f"{s.first_name} {s.last_name}".strip(),
                'class_name': f"{s.current_class.name if s.current_class else 'N/A'} - {s.current_section.name if s.current_section else 'A'}",
                'date': s.admission_date.strftime("%d %b %Y") if s.admission_date else today_formatted,
                'status': s.get_status_display() or 'Active'
            })

        # Real Recent Notices from Database
        db_notices = list(Notice.objects.filter(school=request.school, is_active=True).order_by('-created_at')[:5])
        notices_list = []
        for n in db_notices:
            notices_list.append({
                'icon': 'fa-solid fa-bullhorn',
                'color': '#f97316',
                'title': n.title,
                'date': n.created_at.strftime("%d %b %Y"),
                'desc': n.content[:60] if n.content else '',
                'badge': n.get_target_role_display()
            })

        # Real Student Distribution per Class for Donut Chart
        classes = Class.objects.filter(school=request.school)
        color_palette = ['#3b82f6', '#06b6d4', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6']
        chart_labels = []
        chart_data = []
        chart_colors = []

        for idx, cls in enumerate(classes):
            c_count = Student.objects.filter(school=request.school, current_class=cls, status='ACTIVE').count()
            if c_count > 0:
                chart_labels.append(cls.name)
                chart_data.append(c_count)
                chart_colors.append(color_palette[idx % len(color_palette)])

        if not chart_labels and db_students_count > 0:
            chart_labels = ['Active Students']
            chart_data = [db_students_count]
            chart_colors = ['#3b82f6']

        donut_total = sum(chart_data)
        donut_legend = list(zip(chart_labels, chart_data, chart_colors))

        # Real Monthly Enrollment Trend for Current Academic Session
        months_labels = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
        enrollment_counts = []
        for m in [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]:
            cnt = Student.objects.filter(
                school=request.school,
                admission_date__month=m
            ).count()
            enrollment_counts.append(cnt)

        return render(request, 'dashboard/school_admin.html', {
            'total_students_display': total_students_display,
            'total_teachers_display': total_teachers_display,
            'fee_collected_display': fee_collected_display,
            'defaulters_count_display': defaulters_count_display,
            'pending_verifications_count': pending_verifications_count,
            'total_classes': db_classes_count,
            'today_formatted': today_formatted,
            'today_present': today_present,
            'today_absent': today_absent,
            'today_leave': today_leave,
            'attendance_pct': attendance_pct,
            'notices_list': notices_list,
            'recent_admissions': recent_admissions,
            'active_session': active_session,
            'donut_total': donut_total,
            'donut_legend': donut_legend,
            'chart_labels_json': json.dumps(chart_labels),
            'chart_data_json': json.dumps(chart_data),
            'chart_colors_json': json.dumps(chart_colors),
            'months_labels_json': json.dumps(months_labels),
            'enrollment_counts_json': json.dumps(enrollment_counts),
        })

    # Teacher Dashboard
    if user.is_teacher_user():
        teacher_profile = getattr(user, 'teacher_profile', None)
        assigned_classes = teacher_profile.assigned_classes.all() if teacher_profile else []
        assigned_subjects = teacher_profile.assigned_subjects.all() if teacher_profile else []
        timetables = Timetable.objects.filter(teacher_user=user)
        homeworks = Homework.objects.filter(created_by=user)[:5]
        notices = Notice.objects.filter(school=request.school, is_active=True).filter(Q(target_role='ALL') | Q(target_role='TEACHER'))[:5]

        return render(request, 'dashboard/teacher.html', {
            'teacher': teacher_profile,
            'assigned_classes': assigned_classes,
            'assigned_subjects': assigned_subjects,
            'timetables': timetables,
            'homeworks': homeworks,
            'notices': notices,
        })

    # Student Dashboard
    if user.is_student_user():
        student = getattr(user, 'student_profile', None)
        if not student:
            return render(request, 'dashboard/student.html', {'student': None})

        attendances = student.attendances.all()
        tot_att = attendances.count()
        pres_att = attendances.filter(status='P').count()
        att_pct = round((pres_att / tot_att) * 100, 1) if tot_att > 0 else 100.0

        # Comprehensive Fee Analytics
        from decimal import Decimal
        from fees.models import PaymentSubmission
        today_dt = date.today()
        fees = student.fees.select_related('fee_head', 'academic_session').prefetch_related('submissions').all()
        total_invoiced = sum([f.amount_due for f in fees], Decimal('0.00'))
        total_paid = sum([f.amount_paid for f in fees], Decimal('0.00'))
        total_due = sum([f.net_due for f in fees], Decimal('0.00'))
        total_under_review = sum([f.under_review_amount for f in fees], Decimal('0.00'))
        past_arrears = sum([f.net_due for f in fees if f.due_date and f.due_date < today_dt], Decimal('0.00'))
        current_dues = sum([f.net_due for f in fees if not f.due_date or f.due_date >= today_dt], Decimal('0.00'))

        # Payment submissions history
        submissions = PaymentSubmission.objects.filter(
            school=request.school, student=student
        ).select_related('student_fee__fee_head', 'official_payment').order_by('-submitted_at')[:5]

        # Verified official receipts
        verified_payments = FeePayment.objects.filter(
            school=request.school, student_fee__student=student, status='VERIFIED'
        ).select_related('student_fee__fee_head').order_by('-payment_date')[:5]

        homeworks = Homework.objects.filter(class_level=student.current_class, section=student.current_section)[:5]
        study_materials = StudyMaterial.objects.filter(class_level=student.current_class)[:5]
        notices = Notice.objects.filter(school=request.school, is_active=True).filter(Q(target_role='ALL') | Q(target_role='STUDENT'))[:5]
        marks = student.marks.select_related('exam', 'subject')[:10]
        timetables = Timetable.objects.filter(class_level=student.current_class, section=student.current_section)

        return render(request, 'dashboard/student.html', {
            'student': student,
            'att_pct': att_pct,
            'fees': fees,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'total_due': total_due,
            'total_under_review': total_under_review,
            'past_arrears': past_arrears,
            'current_dues': current_dues,
            'submissions': submissions,
            'verified_payments': verified_payments,
            'homeworks': homeworks,
            'study_materials': study_materials,
            'notices': notices,
            'marks': marks,
            'timetables': timetables,
        })

    # Parent Dashboard
    if user.is_parent_user():
        parent_profile = getattr(user, 'parent_profile', None)
        children = parent_profile.students.all() if parent_profile else []
        notices = Notice.objects.filter(school=request.school, is_active=True).filter(Q(target_role='ALL') | Q(target_role='PARENT'))[:5]

        return render(request, 'dashboard/parent.html', {
            'parent': parent_profile,
            'children': children,
            'notices': notices,
        })

    return redirect('profile')
