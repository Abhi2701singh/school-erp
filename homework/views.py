from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from homework.models import Homework, StudyMaterial
from homework.forms import HomeworkForm, StudyMaterialForm

@login_required
def homework_list_view(request):
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))

    if is_super and not request.school:
        homeworks = Homework.all_objects.all().select_related('class_level', 'section', 'subject', 'created_by')
    else:
        homeworks = Homework.objects.filter(school=request.school).select_related('class_level', 'section', 'subject', 'created_by')

    if request.method == 'POST' and (request.user.is_teacher_user() or request.user.is_school_admin() or is_super):
        form = HomeworkForm(request.POST, request.FILES, school=request.school)
        if form.is_valid():
            hw = form.save(commit=False)
            hw.school = request.school
            hw.created_by = request.user
            hw.save()
            messages.success(request, f"Homework '{hw.title}' assigned successfully!")
            return redirect('homework_list')
    else:
        form = HomeworkForm(school=request.school)

    return render(request, 'homework/homework_list.html', {'homeworks': homeworks, 'form': form})


@login_required
def homework_delete_view(request, pk):
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))
    if is_super and not request.school:
        hw = get_object_or_404(Homework.all_objects, pk=pk)
    else:
        hw = get_object_or_404(Homework, pk=pk, school=request.school)

    if not (request.user.is_teacher_user() or request.user.is_school_admin() or is_super):
        messages.error(request, "Permission denied.")
        return redirect('homework_list')

    if request.method == 'POST':
        title = hw.title
        hw.delete()
        messages.success(request, f"Homework assignment '{title}' deleted successfully.")
        return redirect('homework_list')

    return render(request, 'homework/homework_confirm_delete.html', {'homework': hw})


@login_required
def study_material_list_view(request):
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))

    if is_super and not request.school:
        materials = StudyMaterial.all_objects.all().select_related('class_level', 'subject', 'uploaded_by')
    else:
        materials = StudyMaterial.objects.filter(school=request.school).select_related('class_level', 'subject', 'uploaded_by')

    if request.method == 'POST' and (request.user.is_teacher_user() or request.user.is_school_admin() or is_super):
        form = StudyMaterialForm(request.POST, request.FILES, school=request.school)
        if form.is_valid():
            sm = form.save(commit=False)
            sm.school = request.school
            sm.uploaded_by = request.user
            sm.save()
            messages.success(request, f"Study material '{sm.title}' uploaded successfully!")
            return redirect('study_material_list')
    else:
        form = StudyMaterialForm(school=request.school)

    return render(request, 'homework/study_material_list.html', {'materials': materials, 'form': form})


@login_required
def study_material_delete_view(request, pk):
    is_super = request.user.is_super_admin() if callable(getattr(request.user, 'is_super_admin', None)) else bool(getattr(request.user, 'is_super_admin', False))
    if is_super and not request.school:
        sm = get_object_or_404(StudyMaterial.all_objects, pk=pk)
    else:
        sm = get_object_or_404(StudyMaterial, pk=pk, school=request.school)

    if not (request.user.is_teacher_user() or request.user.is_school_admin() or is_super):
        messages.error(request, "Permission denied.")
        return redirect('study_material_list')

    if request.method == 'POST':
        title = sm.title
        sm.delete()
        messages.success(request, f"Study material '{title}' deleted successfully.")
        return redirect('study_material_list')

    return render(request, 'homework/study_material_confirm_delete.html', {'material': sm})


