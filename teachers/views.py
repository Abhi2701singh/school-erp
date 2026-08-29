from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from teachers.models import Teacher
from teachers.forms import TeacherForm
from accounts.models import User

@login_required
def teacher_list_view(request):
    teachers = Teacher.objects.filter(school=request.school).select_related('user').prefetch_related('assigned_classes', 'assigned_subjects')
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers})


@login_required
def teacher_create_view(request):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('teacher_list')

    if request.method == 'POST':
        form = TeacherForm(request.POST, school=request.school)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password'] or 'Teacher@123'
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' already taken.")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role=User.Roles.TEACHER,
                    school=request.school,
                    password=password
                )
                teacher = form.save(commit=False)
                teacher.school = request.school
                teacher.user = user
                teacher.save()
                form.save_m2m()
                messages.success(request, f"Teacher '{first_name} {last_name}' added successfully! Login: {username} / {password}")
                return redirect('teacher_list')
    else:
        form = TeacherForm(school=request.school)

    return render(request, 'teachers/teacher_form.html', {'form': form, 'title': 'Add Teacher'})


@login_required
def teacher_edit_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk, school=request.school)
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('teacher_list')

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher, school=request.school)
        if form.is_valid():
            user = teacher.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            form.save()
            messages.success(request, "Teacher details updated successfully.")
            return redirect('teacher_list')
    else:
        initial = {
            'username': teacher.user.username,
            'email': teacher.user.email,
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
        }
        form = TeacherForm(instance=teacher, initial=initial, school=request.school)

    return render(request, 'teachers/teacher_form.html', {'form': form, 'title': f'Edit Teacher - {teacher.user.get_full_name()}'})
