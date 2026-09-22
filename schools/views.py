from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.models import User
from schools.models import School, AcademicSession, Notice
from schools.forms import SchoolForm, AcademicSessionForm, NoticeForm

@login_required
def school_list_view(request):
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))
    if not is_super:
        messages.error(request, "Access restricted to Super Admins.")
        return redirect('dashboard')

    schools = School.objects.all()
    # Attach admin user to each school for display
    for s in schools:
        s.admin_user = User.objects.filter(school=s, role__in=[User.Roles.SCHOOL_ADMIN, User.Roles.PRINCIPAL]).first()

    return render(request, 'schools/school_list.html', {'schools': schools})


import datetime

@login_required
def school_create_view(request):
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))
    if not is_super:
        messages.error(request, "Permission denied. Only Super Admin can register schools.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            school = form.save()
            
            # Automatically create initial current Academic Session for new school
            current_year = datetime.date.today().year
            session_name = f"{current_year}-{current_year + 1}"
            AcademicSession.objects.get_or_create(
                school=school,
                name=session_name,
                defaults={
                    'start_date': datetime.date(current_year, 4, 1),
                    'end_date': datetime.date(current_year + 1, 3, 31),
                    'is_current': True
                }
            )

            # Automatically create School Admin user
            admin_username = form.cleaned_data.get('admin_username')
            if not admin_username:
                admin_username = f"admin_{school.code.lower()}"
            else:
                admin_username = admin_username.strip().lower()

            # Ensure admin_username is globally unique
            base_username = admin_username
            counter = 1
            while User.objects.filter(username=admin_username).exists():
                admin_username = f"{base_username}_{counter}"
                counter += 1

            admin_password = form.cleaned_data.get('admin_password') or "Password@123"
            admin_email = school.email or f"{admin_username}@{school.code.lower()}.edu"

            User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                role=User.Roles.SCHOOL_ADMIN,
                school=school,
                first_name=school.name,
                last_name="Admin"
            )

            messages.success(
                request,
                f"School '{school.name}' registered successfully! Admin Login -> Username: '{admin_username}' | Password: '{admin_password}'"
            )
            return redirect('school_list')
        else:
            messages.error(request, "Could not register school. Please review the errors below.")
    else:
        form = SchoolForm(initial={'is_active': True})

    return render(request, 'schools/school_form.html', {'form': form, 'title': 'Register New School'})


@login_required
def school_edit_view(request, pk):
    school = get_object_or_404(School, pk=pk)
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))
    is_admin = request.user.is_school_admin() if callable(getattr(request.user, 'is_school_admin', None)) else bool(getattr(request.user, 'is_school_admin', False))
    if not (is_super or (is_admin and request.user.school == school)):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    admin_user = User.objects.filter(school=school, role__in=[User.Roles.SCHOOL_ADMIN, User.Roles.PRINCIPAL]).first()

    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()

            # If Super Admin updated admin credentials
            if is_super:
                admin_username = form.cleaned_data.get('admin_username')
                admin_password = form.cleaned_data.get('admin_password')

                if admin_user:
                    if admin_username and admin_username != admin_user.username:
                        if not User.objects.filter(username=admin_username).exclude(pk=admin_user.pk).exists():
                            admin_user.username = admin_username
                    if admin_password:
                        admin_user.set_password(admin_password)
                    admin_user.save()
                elif admin_username:
                    User.objects.create_user(
                        username=admin_username,
                        password=admin_password or 'Password@123',
                        role=User.Roles.SCHOOL_ADMIN,
                        school=school,
                        first_name=school.name,
                        last_name="Admin"
                    )

            messages.success(request, f"School '{school.name}' details updated.")
            return redirect('school_list' if is_super else 'dashboard')
    else:
        initial = {}
        if admin_user:
            initial['admin_username'] = admin_user.username
        form = SchoolForm(instance=school, initial=initial)

    return render(request, 'schools/school_form.html', {'form': form, 'title': f'Edit {school.name}', 'school': school, 'admin_user': admin_user})


@login_required
def school_delete_view(request, pk):
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))
    if not is_super:
        messages.error(request, "Permission denied. Only Super Admin can delete schools.")
        return redirect('dashboard')

    school = get_object_or_404(School, pk=pk)
    if request.method == 'POST':
        school_name = school.name
        school.delete()
        messages.success(request, f"School '{school_name}' and all its associated data (students, teachers, classes, records) have been permanently deleted.")
        return redirect('school_list')

    return render(request, 'schools/school_confirm_delete.html', {'school': school})


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
def session_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    session = get_object_or_404(AcademicSession, pk=pk, school=request.school)
    if request.method == 'POST':
        s_name = session.name
        session.delete()
        messages.success(request, f"Academic session '{s_name}' deleted successfully.")
        return redirect('session_list')

    return render(request, 'schools/session_confirm_delete.html', {'session': session})


@login_required
def notice_list_view(request):
    user = request.user
    if user.is_super_admin():
        notices = Notice.objects.all()
    elif user.is_teacher_user():
        notices = Notice.objects.filter(school=request.school, is_active=True).filter(Q(target_role='ALL') | Q(target_role='TEACHER'))
    elif user.is_student_user():
        notices = Notice.objects.filter(school=request.school, is_active=True).filter(Q(target_role='ALL') | Q(target_role='STUDENT'))
    elif user.is_parent_user():
        notices = Notice.objects.filter(school=request.school, is_active=True).filter(Q(target_role='ALL') | Q(target_role='PARENT'))
    else:
        # School Admin / Principal: see all notices of this school
        notices = Notice.objects.filter(school=request.school)

    if request.method == 'POST':
        if not (user.is_school_admin() or user.is_super_admin()):
            messages.error(request, "Permission denied. Only School Admin/Principal can post notices.")
            return redirect('notice_list')

        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.school = request.school
            notice.is_active = True
            notice.save()
            messages.success(request, "Notice published successfully!")
            return redirect('notice_list')
    else:
        form = NoticeForm()

    return render(request, 'schools/notice_list.html', {'notices': notices, 'form': form})


@login_required
def notice_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    notice = get_object_or_404(Notice, pk=pk, school=request.school)
    if request.method == 'POST':
        notice.delete()
        messages.success(request, "Notice deleted successfully.")
        return redirect('notice_list')

    return render(request, 'schools/notice_confirm_delete.html', {'notice': notice})
