from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from homework.models import Homework, StudyMaterial
from homework.forms import HomeworkForm, StudyMaterialForm

@login_required
def homework_list_view(request):
    homeworks = Homework.objects.select_related('class_level', 'section', 'subject', 'created_by').all()

    if request.method == 'POST' and (request.user.is_teacher_user() or request.user.is_school_admin()):
        form = HomeworkForm(request.POST, request.FILES)
        if form.is_valid():
            hw = form.save(commit=False)
            hw.school = request.school
            hw.created_by = request.user
            hw.save()
            messages.success(request, "Homework assigned successfully!")
            return redirect('homework_list')
    else:
        form = HomeworkForm()

    return render(request, 'homework/homework_list.html', {'homeworks': homeworks, 'form': form})


@login_required
def study_material_list_view(request):
    materials = StudyMaterial.objects.select_related('class_level', 'subject', 'uploaded_by').all()

    if request.method == 'POST' and (request.user.is_teacher_user() or request.user.is_school_admin()):
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            sm = form.save(commit=False)
            sm.school = request.school
            sm.uploaded_by = request.user
            sm.save()
            messages.success(request, "Study material uploaded!")
            return redirect('study_material_list')
    else:
        form = StudyMaterialForm()

    return render(request, 'homework/study_material_list.html', {'materials': materials, 'form': form})
