from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import Class, Section, Subject, Timetable
from academics.forms import ClassForm, SectionForm, SubjectForm, TimetableForm

@login_required
def class_list_view(request):
    classes = Class.objects.filter(school=request.school)
    if request.method == 'POST' and request.user.is_school_admin():
        form = ClassForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data.get('name')
            # Check duplicate class
            if Class.objects.filter(school=request.school, name=class_name).exists():
                messages.warning(request, f"Class '{class_name}' already exists in your school!")
                return redirect('class_list')

            cls = form.save(commit=False)
            cls.school = request.school
            cls.save()
            # Automatically create section 'A' for the newly created class
            Section.objects.create(school=request.school, class_level=cls, name='A', stream='General')
            messages.success(request, f"Class '{cls.name}' added with default Section A!")
            return redirect('class_list')
    else:
        form = ClassForm()

    return render(request, 'academics/class_list.html', {'classes': classes, 'form': form})


@login_required
def class_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('class_list')

    cls = get_object_or_404(Class, pk=pk, school=request.school)
    if request.method == 'POST':
        class_name = cls.name
        cls.delete()
        messages.success(request, f"Class '{class_name}' and its sections have been deleted successfully.")
        return redirect('class_list')

    return render(request, 'academics/class_confirm_delete.html', {'cls': cls})


@login_required
def section_list_view(request):
    sections = Section.objects.filter(school=request.school).select_related('class_level')
    if request.method == 'POST' and request.user.is_school_admin():
        form = SectionForm(request.POST, school=request.school)
        if form.is_valid():
            sec = form.save(commit=False)
            sec.school = request.school
            sec.save()
            messages.success(request, f"Section '{sec.name}' added to {sec.class_level.name}!")
            return redirect('section_list')
    else:
        form = SectionForm(school=request.school)

    return render(request, 'academics/section_list.html', {'sections': sections, 'form': form})


@login_required
def section_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('section_list')

    section = get_object_or_404(Section, pk=pk, school=request.school)
    if request.method == 'POST':
        sec_name = f"{section.class_level.name} - Section {section.name}"
        section.delete()
        messages.success(request, f"Section '{sec_name}' deleted successfully.")
        return redirect('section_list')

    return render(request, 'academics/section_confirm_delete.html', {'section': section})


@login_required
def subject_list_view(request):
    subjects = Subject.objects.filter(school=request.school)
    if request.method == 'POST' and request.user.is_school_admin():
        form = SubjectForm(request.POST)
        if form.is_valid():
            sbj = form.save(commit=False)
            sbj.school = request.school
            sbj.save()
            messages.success(request, f"Subject '{sbj.name}' created.")
            return redirect('subject_list')
    else:
        form = SubjectForm()

    return render(request, 'academics/subject_list.html', {'subjects': subjects, 'form': form})


@login_required
def subject_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('subject_list')

    subject = get_object_or_404(Subject, pk=pk, school=request.school)
    if request.method == 'POST':
        subj_name = subject.name
        subject.delete()
        messages.success(request, f"Subject '{subj_name}' deleted successfully.")
        return redirect('subject_list')

    return render(request, 'academics/subject_confirm_delete.html', {'subject': subject})


@login_required
def timetable_view(request):
    timetables = Timetable.objects.filter(school=request.school).select_related('class_level', 'section', 'subject', 'teacher_user')
    class_id = request.GET.get('class_id')
    section_id = request.GET.get('section_id')

    if class_id:
        timetables = timetables.filter(class_level_id=class_id)
    if section_id:
        timetables = timetables.filter(section_id=section_id)

    if request.method == 'POST' and request.user.is_school_admin():
        form = TimetableForm(request.POST, school=request.school)
        if form.is_valid():
            tt = form.save(commit=False)
            tt.school = request.school
            tt.save()
            messages.success(request, "Timetable period added.")
            return redirect('timetable')
    else:
        form = TimetableForm(school=request.school)

    classes = Class.objects.filter(school=request.school)
    sections = Section.objects.filter(school=request.school)

    return render(request, 'academics/timetable.html', {
        'timetables': timetables,
        'form': form,
        'classes': classes,
        'sections': sections,
        'selected_class': class_id,
        'selected_section': section_id,
    })


@login_required
def timetable_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('timetable')

    tt = get_object_or_404(Timetable, pk=pk, school=request.school)
    if request.method == 'POST':
        tt.delete()
        messages.success(request, "Timetable period deleted.")
        return redirect('timetable')

    return render(request, 'academics/timetable_confirm_delete.html', {'timetable': tt})
