from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from schools.models import School, AcademicSession, Notice
from schools.forms import SchoolForm, AcademicSessionForm, NoticeForm

@login_required
def school_list_view(request):
    if not request.user.is_super_admin():
        messages.error(request, "Access restricted to Super Admins.")
        return redirect('dashboard')

    schools = School.objects.all()
    return render(request, 'schools/school_list.html', {'schools': schools})


@login_required
def school_create_view(request):
    if not request.user.is_super_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            school = form.save()
            # Automatically create initial 2025-2026 Academic Session for new school
            AcademicSession.objects.create(
                school=school,
                name="2025-2026",
                start_date="2025-04-01",
                end_date="2026-03-31",
                is_current=True
            )
            messages.success(request, f"School '{school.name}' created successfully with initial Academic Session 2025-2026!")
            return redirect('school_list')
    else:
        form = SchoolForm()

    return render(request, 'schools/school_form.html', {'form': form, 'title': 'Add New School'})


@login_required
def school_edit_view(request, pk):
    school = get_object_or_404(School, pk=pk)
    if not (request.user.is_super_admin() or (request.user.is_school_admin() and request.user.school == school)):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, f"School '{school.name}' details updated.")
            return redirect('dashboard')
    else:
        form = SchoolForm(instance=school)

    return render(request, 'schools/school_form.html', {'form': form, 'title': f'Edit {school.name}', 'school': school})


@login_required
def session_list_view(request):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    sessions = AcademicSession.objects.filter(school=request.school)
    if request.method == 'POST':
        form = AcademicSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.school = request.school
            session.save()
            messages.success(request, f"Academic session '{session.name}' added.")
            return redirect('session_list')
    else:
        form = AcademicSessionForm()

    return render(request, 'schools/session_list.html', {'sessions': sessions, 'form': form})


@login_required
def notice_list_view(request):
    if request.user.is_super_admin():
        notices = Notice.objects.all()
    else:
        notices = Notice.objects.filter(school=request.school, is_active=True)

    if request.method == 'POST' and request.user.is_school_admin():
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.school = request.school
            notice.save()
            messages.success(request, "Notice published successfully!")
            return redirect('notice_list')
    else:
        form = NoticeForm()

    return render(request, 'schools/notice_list.html', {'notices': notices, 'form': form})
