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

    students = Student.objects.filter(school=request.school).select_related('current_class', 'current_section', 'academic_session')

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

    classes = Class.objects.filter(school=request.school)
    sections = Section.objects.filter(school=request.school)

    return render(request, 'students/student_list.html', {
        'students': students,
        'classes': classes,
        'sections': sections,
        'query': query,
        'selected_class': class_id,
        'selected_section': section_id,
    })


from datetime import date

@login_required
def student_admission_view(request):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('student_list')

    # Ensure school has an active academic session
    active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()
    if not active_session:
        active_session = AcademicSession.objects.filter(school=request.school).first()
    if not active_session:
        active_session = AcademicSession.objects.create(
            school=request.school,
            name="2025-2026",
            start_date=date(2025, 4, 1),
            end_date=date(2026, 3, 31),
            is_current=True
        )

    if request.method == 'POST':
        form = StudentAdmissionForm(request.POST, request.FILES, school=request.school)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = request.school

            if not student.academic_session_id:
                student.academic_session = active_session

            if not student.admission_date:
                student.admission_date = date.today()

            # Auto-generate admission_no if not provided
            if not student.admission_no:
                total_existing = Student.objects.filter(school=request.school).count() + 1
                student.admission_no = f"ADM{date.today().year}-{total_existing:03d}"

            # 1. Student Login Username = Student's Name (lowercase)
            name_slug = f"{student.first_name}".strip().lower().replace(" ", "")
            if student.last_name:
                name_slug_full = f"{student.first_name}{student.last_name}".strip().lower().replace(" ", "")
            else:
                name_slug_full = name_slug

            username = name_slug
            if User.objects.filter(username=username).exists():
                username = name_slug_full
            
            counter = 1
            while User.objects.filter(username=username).exists():
                clean_adm = student.admission_no.lower().replace("-", "").replace(" ", "")
                username = f"{name_slug}_{clean_adm}"
                if not User.objects.filter(username=username).exists():
                    break
                username = f"{name_slug}_{counter}"
                counter += 1

            # 2. Student Login Password = Date of Birth (DOB) e.g. 15-08-2015
            dob_password = student.dob.strftime('%d-%m-%Y') if student.dob else "Password@123"

            user = User.objects.create_user(
                username=username,
                first_name=student.first_name,
                last_name=student.last_name,
                email=student.parent_email or f"{username}@{request.school.code.lower()}.edu",
                role=User.Roles.STUDENT,
                school=request.school,
                password=dob_password
            )
            student.user = user
            student.save()

            messages.success(
                request,
                f"Student '{student.first_name} {student.last_name}' admitted successfully! "
                f"Login Username: '{username}' | Password (DOB): '{dob_password}'"
            )
            return redirect('student_list')
        else:
            messages.error(request, "Please check the form and correct the errors below.")
    else:
        initial = {'academic_session': active_session, 'admission_date': date.today(), 'gender': 'M'}
        form = StudentAdmissionForm(initial=initial, school=request.school)

    return render(request, 'students/student_admission.html', {'form': form, 'active_session': active_session})


@login_required
def student_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('student_list')

    student = get_object_or_404(Student, pk=pk, school=request.school)
    if request.method == 'POST':
        student_name = f"{student.first_name} {student.last_name}".strip()
        adm_no = student.admission_no
        # Also delete linked user account if exists
        if student.user:
            student.user.delete()
        student.delete()
        messages.success(request, f"Student '{student_name}' (Adm: {adm_no}) deleted successfully.")
        return redirect('student_list')

    return render(request, 'students/student_confirm_delete.html', {'student': student})


@login_required
def student_profile_view(request, pk):
    if request.user.is_super_admin():
        student = get_object_or_404(Student.objects.select_related('current_class', 'current_section', 'academic_session', 'school', 'user'), pk=pk)
    else:
        student = get_object_or_404(Student.objects.select_related('current_class', 'current_section', 'academic_session', 'school', 'user'), pk=pk, school=request.school)

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
    dob_password = student.dob.strftime('%d-%m-%Y') if student.dob else "-"

    return render(request, 'students/student_profile.html', {
        'student': student,
        'doc_form': doc_form,
        'documents': documents,
        'attendances': attendances,
        'fees': fees,
        'marks': marks,
        'attendance_pct': attendance_pct,
        'dob_password': dob_password,
    })


@login_required
def student_id_card_view(request, pk):
    if request.user.is_super_admin():
        student = get_object_or_404(Student.objects.select_related('current_class', 'current_section', 'school'), pk=pk)
    else:
        student = get_object_or_404(Student.objects.select_related('current_class', 'current_section', 'school'), pk=pk, school=request.school)
    return render(request, 'students/student_id_card.html', {'student': student})
