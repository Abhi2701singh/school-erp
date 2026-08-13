from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from attendance.models import StudentAttendance
from students.models import Student
from academics.models import Class, Section
from schools.models import AcademicSession

@login_required
def mark_attendance_view(request):
    class_id = request.GET.get('class_id')
    section_id = request.GET.get('section_id')
    attendance_date_str = request.GET.get('date', str(date.today()))

    classes = Class.objects.all()
    sections = Section.objects.all()
    active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()

    students = []
    existing_attendance = {}

    if class_id and section_id:
        students = Student.objects.filter(current_class_id=class_id, current_section_id=section_id, status='ACTIVE')
        records = StudentAttendance.objects.filter(
            class_level_id=class_id,
            section_id=section_id,
            date=attendance_date_str
        )
        existing_attendance = {r.student_id: r.status for r in records}

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        section_id = request.POST.get('section_id')
        attendance_date_str = request.POST.get('date')

        if not active_session:
            messages.error(request, "No active academic session found for this school.")
            return redirect('mark_attendance')

        students = Student.objects.filter(current_class_id=class_id, current_section_id=section_id, status='ACTIVE')
        saved_count = 0

        for student in students:
            status_val = request.POST.get(f'status_{student.id}', 'P')
            remarks_val = request.POST.get(f'remarks_{student.id}', '')

            StudentAttendance.objects.update_or_create(
                school=request.school,
                academic_session=active_session,
                date=attendance_date_str,
                student=student,
                defaults={
                    'class_level_id': class_id,
                    'section_id': section_id,
                    'status': status_val,
                    'remarks': remarks_val,
                    'marked_by': request.user
                }
            )
            saved_count += 1

        messages.success(request, f"Attendance saved for {saved_count} students on {attendance_date_str}!")
        return redirect(f"/attendance/mark/?class_id={class_id}&section_id={section_id}&date={attendance_date_str}")

    return render(request, 'attendance/mark_attendance.html', {
        'classes': classes,
        'sections': sections,
        'selected_class': class_id,
        'selected_section': section_id,
        'attendance_date': attendance_date_str,
        'students': students,
        'existing_attendance': existing_attendance,
    })


@login_required
def attendance_report_view(request):
    class_id = request.GET.get('class_id')
    section_id = request.GET.get('section_id')
    month = request.GET.get('month', date.today().month)
    year = request.GET.get('year', date.today().year)

    classes = Class.objects.all()
    sections = Section.objects.all()

    report_data = []
    if class_id and section_id:
        students = Student.objects.filter(current_class_id=class_id, current_section_id=section_id, status='ACTIVE')
        for student in students:
            atts = StudentAttendance.objects.filter(
                student=student,
                date__month=month,
                date__year=year
            )
            total = atts.count()
            present = atts.filter(status='P').count()
            absent = atts.filter(status='A').count()
            leave = atts.filter(status__in=['L', 'LE', 'H']).count()
            pct = round((present / total) * 100, 1) if total > 0 else 100.0

            report_data.append({
                'student': student,
                'total': total,
                'present': present,
                'absent': absent,
                'leave': leave,
                'pct': pct,
            })

    return render(request, 'attendance/attendance_report.html', {
        'classes': classes,
        'sections': sections,
        'selected_class': class_id,
        'selected_section': section_id,
        'report_data': report_data,
        'month': int(month),
        'year': int(year),
    })
