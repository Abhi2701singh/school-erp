from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
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
        total_students_all = Student.objects.count()
        total_teachers_all = Teacher.objects.count()
        schools = School.objects.all()

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

        total_students = Student.objects.filter(status='ACTIVE').count()
        total_teachers = Teacher.objects.count()
        total_classes = Class.objects.count()

        today_str = date.today()
        today_atts = StudentAttendance.objects.filter(date=today_str)
        today_present = today_atts.filter(status='P').count()
        today_absent = today_atts.filter(status='A').count()
        today_total = today_atts.count()
        attendance_pct = round((today_present / today_total) * 100, 1) if today_total > 0 else 0.0

        # Fee Analytics
        fee_collected_total = FeePayment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0.0
        pending_fees = StudentFee.objects.filter(status__in=['PENDING', 'PARTIAL'])
        defaulters_count = pending_fees.values('student').distinct().count()

        notices = Notice.objects.filter(is_active=True)[:5]
        recent_students = Student.objects.order_by('-created_at')[:5]

        return render(request, 'dashboard/school_admin.html', {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'today_present': today_present,
            'today_absent': today_absent,
            'attendance_pct': attendance_pct,
            'fee_collected_total': fee_collected_total,
            'defaulters_count': defaulters_count,
            'notices': notices,
            'recent_students': recent_students,
            'active_session': active_session,
        })

    # Teacher Dashboard
    if user.is_teacher_user():
        teacher_profile = getattr(user, 'teacher_profile', None)
        assigned_classes = teacher_profile.assigned_classes.all() if teacher_profile else []
        assigned_subjects = teacher_profile.assigned_subjects.all() if teacher_profile else []
        timetables = Timetable.objects.filter(teacher_user=user)
        homeworks = Homework.objects.filter(created_by=user)[:5]
        notices = Notice.objects.filter(Q(target_role='ALL') | Q(target_role='TEACHER'), is_active=True)[:5]

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

        fees = student.fees.all()
        total_due = sum([f.net_due for f in fees])

        homeworks = Homework.objects.filter(class_level=student.current_class, section=student.current_section)[:5]
        study_materials = StudyMaterial.objects.filter(class_level=student.current_class)[:5]
        notices = Notice.objects.filter(Q(target_role='ALL') | Q(target_role='STUDENT'), is_active=True)[:5]
        marks = student.marks.select_related('exam', 'subject')[:10]
        timetables = Timetable.objects.filter(class_level=student.current_class, section=student.current_section)

        return render(request, 'dashboard/student.html', {
            'student': student,
            'att_pct': att_pct,
            'total_due': total_due,
            'fees': fees,
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
        notices = Notice.objects.filter(Q(target_role='ALL') | Q(target_role='PARENT'), is_active=True)[:5]

        return render(request, 'dashboard/parent.html', {
            'parent': parent_profile,
            'children': children,
            'notices': notices,
        })

    return redirect('profile')
