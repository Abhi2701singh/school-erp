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
    classes = Class.objects.filter(school=request.school)
    sections = Section.objects.filter(school=request.school)

    selected_class_id = request.GET.get('class_id')
    selected_section_id = request.GET.get('section_id')

    # Auto-resolve class & section if not provided
    if request.user.is_student_user() and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        if not selected_class_id and student.current_class_id:
            selected_class_id = str(student.current_class_id)
        if not selected_section_id and student.current_section_id:
            selected_section_id = str(student.current_section_id)
    elif request.user.is_parent_user():
        first_child = request.user.children.first()
        if first_child:
            if not selected_class_id and first_child.current_class_id:
                selected_class_id = str(first_child.current_class_id)
            if not selected_section_id and first_child.current_section_id:
                selected_section_id = str(first_child.current_section_id)

    if not selected_class_id and classes.exists():
        first_tt = Timetable.objects.filter(school=request.school).first()
        if first_tt:
            selected_class_id = str(first_tt.class_level_id)
            if not selected_section_id:
                selected_section_id = str(first_tt.section_id)
        else:
            selected_class_id = str(classes.first().id)

    if selected_class_id and not selected_section_id:
        first_sec = sections.filter(class_level_id=selected_class_id).first()
        if first_sec:
            selected_section_id = str(first_sec.id)

    # Filter timetables for the selected class and section
    timetables_qs = Timetable.objects.filter(school=request.school).select_related('class_level', 'section', 'subject', 'teacher_user')
    if selected_class_id:
        timetables_qs = timetables_qs.filter(class_level_id=selected_class_id)
    if selected_section_id:
        timetables_qs = timetables_qs.filter(section_id=selected_section_id)

    selected_class_obj = None
    selected_section_obj = None
    if selected_class_id:
        selected_class_obj = classes.filter(id=selected_class_id).first()
    if selected_section_id:
        selected_section_obj = sections.filter(id=selected_section_id).first()

    # Form handling (Add Timetable Period)
    if request.method == 'POST' and request.user.is_school_admin():
        form = TimetableForm(request.POST, school=request.school)
        if form.is_valid():
            tt = form.save(commit=False)
            tt.school = request.school
            tt.save()
            messages.success(request, f"Timetable period for '{tt.subject.name}' added successfully.")
            return redirect(f"/academics/timetable/?class_id={tt.class_level_id}&section_id={tt.section_id}")
    else:
        initial_data = {}
        if selected_class_id:
            initial_data['class_level'] = selected_class_id
        if selected_section_id:
            initial_data['section'] = selected_section_id
        form = TimetableForm(school=request.school, initial=initial_data)

    DAYS_LIST = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    MORNING_PERIODS = [1, 2, 3, 4]
    AFTERNOON_PERIODS = [5, 6, 7, 8, 9]

    # Map existing timetables by (day, period_number)
    tt_map = {}
    for tt in timetables_qs:
        tt_map[(tt.day, tt.period_number)] = tt

    grid_rows = []
    for day in DAYS_LIST:
        morning_cells = []
        for p in MORNING_PERIODS:
            morning_cells.append({
                'period': p,
                'item': tt_map.get((day, p)),
            })

        afternoon_cells = []
        for p in AFTERNOON_PERIODS:
            afternoon_cells.append({
                'period': p,
                'item': tt_map.get((day, p)),
            })

        grid_rows.append({
            'day': day,
            'day_display': day.upper(),
            'morning': morning_cells,
            'afternoon': afternoon_cells,
        })

    return render(request, 'academics/timetable.html', {
        'grid_rows': grid_rows,
        'timetables': timetables_qs,
        'form': form,
        'classes': classes,
        'sections': sections,
        'selected_class': selected_class_id,
        'selected_section': selected_section_id,
        'selected_class_obj': selected_class_obj,
        'selected_section_obj': selected_section_obj,
        'morning_periods': MORNING_PERIODS,
        'afternoon_periods': AFTERNOON_PERIODS,
    })


@login_required
def timetable_delete_view(request, pk):
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('timetable')

    tt = get_object_or_404(Timetable, pk=pk, school=request.school)
    class_id = tt.class_level_id
    section_id = tt.section_id

    if request.method == 'POST' or request.GET.get('confirm') == '1':
        tt.delete()
        messages.success(request, "Timetable period deleted successfully.")
        return redirect(f"/academics/timetable/?class_id={class_id}&section_id={section_id}")

    return render(request, 'academics/timetable_confirm_delete.html', {'timetable': tt})

