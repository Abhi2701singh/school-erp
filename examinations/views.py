from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from examinations.models import Exam, MarksEntry
from examinations.forms import ExamForm
from academics.models import Class, Section, Subject
from students.models import Student
from schools.models import AcademicSession

@login_required
def exam_list_view(request):
    exams = Exam.objects.select_related('class_level', 'academic_session').all()

    if request.method == 'POST' and request.user.is_school_admin():
        form = ExamForm(request.POST)
        if form.is_valid():
            active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()
            if not active_session:
                messages.error(request, "No active academic session found.")
                return redirect('exam_list')

            exam = form.save(commit=False)
            exam.school = request.school
            exam.academic_session = active_session
            exam.save()
            messages.success(request, f"Exam '{exam.name}' created.")
            return redirect('exam_list')
    else:
        form = ExamForm()

    return render(request, 'examinations/exam_list.html', {'exams': exams, 'form': form})


@login_required
def marks_entry_view(request):
    exam_id = request.GET.get('exam_id')
    subject_id = request.GET.get('subject_id')
    section_id = request.GET.get('section_id')

    exams = Exam.objects.all()
    subjects = Subject.objects.all()
    sections = Section.objects.all()

    selected_exam = get_object_or_404(Exam, pk=exam_id) if exam_id else None
    selected_subject = get_object_or_404(Subject, pk=subject_id) if subject_id else None

    students = []
    existing_marks = {}

    if selected_exam and selected_subject and section_id:
        students = Student.objects.filter(
            current_class=selected_exam.class_level,
            current_section_id=section_id,
            status='ACTIVE'
        )
        entries = MarksEntry.objects.filter(
            exam=selected_exam,
            subject=selected_subject,
            student__in=students
        )
        existing_marks = {m.student_id: m for m in entries}

    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        subject_id = request.POST.get('subject_id')
        section_id = request.POST.get('section_id')

        selected_exam = get_object_or_404(Exam, pk=exam_id)
        selected_subject = get_object_or_404(Subject, pk=subject_id)
        students = Student.objects.filter(current_class=selected_exam.class_level, current_section_id=section_id, status='ACTIVE')

        saved_count = 0
        for student in students:
            theory = request.POST.get(f'theory_{student.id}', 0.0)
            practical = request.POST.get(f'practical_{student.id}', 0.0)
            remarks = request.POST.get(f'remarks_{student.id}', '')

            entry, created = MarksEntry.objects.get_or_create(
                school=request.school,
                exam=selected_exam,
                student=student,
                subject=selected_subject,
                defaults={'entered_by': request.user}
            )
            entry.theory_marks_obtained = float(theory or 0)
            entry.practical_marks_obtained = float(practical or 0)
            entry.remarks = remarks
            entry.entered_by = request.user
            entry.save()
            saved_count += 1

        messages.success(request, f"Marks updated for {saved_count} students in {selected_subject.name}!")
        return redirect(f"/examinations/marks/?exam_id={exam_id}&subject_id={subject_id}&section_id={section_id}")

    return render(request, 'examinations/marks_entry.html', {
        'exams': exams,
        'subjects': subjects,
        'sections': sections,
        'selected_exam': selected_exam,
        'selected_subject': selected_subject,
        'selected_section': section_id,
        'students': students,
        'existing_marks': existing_marks,
    })


@login_required
def report_card_view(request, student_id, exam_id):
    student = get_object_or_404(Student.objects.select_related('current_class', 'current_section', 'school'), pk=student_id)
    exam = get_object_or_404(Exam, pk=exam_id)

    marks = MarksEntry.objects.filter(student=student, exam=exam).select_related('subject')

    grand_total_max = sum([m.subject.max_marks for m in marks])
    grand_total_obtained = sum([m.total_marks_obtained for m in marks])

    pct = (float(grand_total_obtained) / float(grand_total_max)) * 100.0 if grand_total_max > 0 else 0.0
    overall_pass = all([m.is_pass for m in marks]) if marks else True

    return render(request, 'examinations/report_card.html', {
        'student': student,
        'exam': exam,
        'marks': marks,
        'grand_total_max': grand_total_max,
        'grand_total_obtained': grand_total_obtained,
        'percentage': round(pct, 2),
        'overall_pass': overall_pass,
    })
