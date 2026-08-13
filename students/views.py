from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from students.models import Student, StudentDocument
from students.forms import StudentAdmissionForm, StudentDocumentForm
from academics.models import Class, Section
from schools.models import AcademicSession
from accounts.models import User

@login_required
def student_list_view(request):
    query = request.GET.get('q', '')
    class_id = request.GET.get('class_id', '')
    section_id = request.GET.get('section_id', '')

    students = Student.objects.select_related('current_class', 'current_section', 'academic_session').all()

    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(admission_no__icontains=query) |
            Q(father_name__icontains=query) |
            Q(parent_phone__icontains=query)
        )
    if class_id:
        students = students.filter(current_class_id=class_id)
    if section_id:
        students = students.filter(current_section_id=section_id)

    classes = Class.objects.all()
    sections = Section.objects.all()

    return render(request, 'students/student_list.html', {
        'students': students,
        'classes': classes,
        'sections': sections,
        'query': query,
        'selected_class': class_id,
        'selected_section': section_id,
    })


@login_required
def student_admission_view(request):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('student_list')

    if request.method == 'POST':
        form = StudentAdmissionForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = request.school

            # Optionally create user credentials for student
            username = f"{request.school.code.lower()}_{student.admission_no.lower()}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    first_name=student.first_name,
                    last_name=student.last_name,
                    email=student.parent_email or f"{username}@school.com",
                    role=User.Roles.STUDENT,
                    school=request.school,
                    password="Password@123"
                )
                student.user = user

            student.save()
            messages.success(request, f"Student '{student.first_name} {student.last_name}' admitted successfully! Credentials: {username} / Password@123")
            return redirect('student_profile', pk=student.pk)
    else:
        # Pre-fill active session if available
        active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()
        initial = {'academic_session': active_session} if active_session else {}
        form = StudentAdmissionForm(initial=initial)

    return render(request, 'students/student_admission.html', {'form': form})


@login_required
def student_profile_view(request, pk):
    student = get_object_or_404(Student.objects.select_related('current_class', 'current_section', 'academic_session', 'school'), pk=pk)

    if request.method == 'POST' and request.user.is_school_admin():
        doc_form = StudentDocumentForm(request.POST, request.FILES)
        if doc_form.is_valid():
            doc = doc_form.save(commit=False)
            doc.school = request.school
            doc.student = student
            doc.save()
            messages.success(request, "Document uploaded.")
            return redirect('student_profile', pk=student.pk)
    else:
        doc_form = StudentDocumentForm()

    documents = student.documents.all()
    attendances = student.attendances.all()[:30]
    fees = student.fees.all()
    marks = student.marks.select_related('exam', 'subject').all()

    # Calculate overall attendance percentage
    total_att = student.attendances.count()
    present_att = student.attendances.filter(status='P').count()
    attendance_pct = round((present_att / total_att) * 100, 1) if total_att > 0 else 100.0

    return render(request, 'students/student_profile.html', {
        'student': student,
        'doc_form': doc_form,
        'documents': documents,
        'attendances': attendances,
        'fees': fees,
        'marks': marks,
        'attendance_pct': attendance_pct,
    })


@login_required
def student_id_card_view(request, pk):
    student = get_object_or_404(Student.objects.select_related('current_class', 'current_section', 'school'), pk=pk)
    return render(request, 'students/student_id_card.html', {'student': student})
