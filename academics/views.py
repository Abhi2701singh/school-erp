from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from schools.models import School
from academics.models import Class, Section, Subject, Timetable, TimetableSetting
from academics.forms import ClassForm, SectionForm, SubjectForm, TimetableForm

def get_period_ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

@login_required
def class_list_view(request):
    school = getattr(request, 'school', None) or (request.user.school if request.user.is_authenticated else None) or School.objects.first()
    classes = Class.objects.filter(school=school) if school else Class.objects.none()
    if request.method == 'POST' and request.user.is_school_admin():
        form = ClassForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data.get('name')
            # Check duplicate class
            if Class.objects.filter(school=school, name=class_name).exists():
                messages.warning(request, f"Class '{class_name}' already exists in your school!")
                return redirect('class_list')

            cls = form.save(commit=False)
            cls.school = school
            cls.save()
            # Automatically create section 'A' for the newly created class
            Section.objects.create(school=school, class_level=cls, name='A', stream='General')
            messages.success(request, f"Class '{cls.name}' added with default Section A!")
            return redirect('class_list')
    else:
        form = ClassForm()

    return render(request, 'academics/class_list.html', {'classes': classes, 'form': form})


@login_required
def class_delete_view(request, pk):
    school = getattr(request, 'school', None) or (request.user.school if request.user.is_authenticated else None) or School.objects.first()
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('class_list')

    cls = get_object_or_404(Class, pk=pk, school=school)
    if request.method == 'POST':
        class_name = cls.name
        cls.delete()
        messages.success(request, f"Class '{class_name}' and its sections have been deleted successfully.")
        return redirect('class_list')

    return render(request, 'academics/class_confirm_delete.html', {'cls': cls})


@login_required
def section_list_view(request):
    school = getattr(request, 'school', None) or (request.user.school if request.user.is_authenticated else None) or School.objects.first()
    sections = Section.objects.filter(school=school).select_related('class_level') if school else Section.objects.none()
    if request.method == 'POST' and request.user.is_school_admin():
        form = SectionForm(request.POST, school=school)
        if form.is_valid():
            sec = form.save(commit=False)
            sec.school = school
            sec.save()
            messages.success(request, f"Section '{sec.name}' added to {sec.class_level.name}!")
            return redirect('section_list')
    else:
        form = SectionForm(school=school)

    return render(request, 'academics/section_list.html', {'sections': sections, 'form': form})


@login_required
def section_delete_view(request, pk):
    school = getattr(request, 'school', None) or (request.user.school if request.user.is_authenticated else None) or School.objects.first()
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('section_list')

    section = get_object_or_404(Section, pk=pk, school=school)
    if request.method == 'POST':
        sec_name = f"{section.class_level.name} - Section {section.name}"
        section.delete()
        messages.success(request, f"Section '{sec_name}' deleted successfully.")
        return redirect('section_list')

    return render(request, 'academics/section_confirm_delete.html', {'section': section})


@login_required
def subject_list_view(request):
    school = getattr(request, 'school', None) or (request.user.school if request.user.is_authenticated else None) or School.objects.first()
    subjects = Subject.objects.filter(school=school) if school else Subject.objects.none()
    if request.method == 'POST' and request.user.is_school_admin():
        form = SubjectForm(request.POST)
        if form.is_valid():
            sbj = form.save(commit=False)
            sbj.school = school
            sbj.save()
            messages.success(request, f"Subject '{sbj.name}' created.")
            return redirect('subject_list')
    else:
        form = SubjectForm()

    return render(request, 'academics/subject_list.html', {'subjects': subjects, 'form': form})


@login_required
def subject_delete_view(request, pk):
    school = getattr(request, 'school', None) or (request.user.school if request.user.is_authenticated else None) or School.objects.first()
    if not request.user.is_school_admin():
        messages.error(request, "Permission denied.")
        return redirect('subject_list')

    subject = get_object_or_404(Subject, pk=pk, school=school)
    if request.method == 'POST':
        subj_name = subject.name
        subject.delete()
        messages.success(request, f"Subject '{subj_name}' deleted successfully.")
        return redirect('subject_list')

    return render(request, 'academics/subject_confirm_delete.html', {'subject': subject})


@login_required
def timetable_view(request):
    school = getattr(request, 'school', None) or (request.user.school if request.user.is_authenticated else None) or School.objects.first()
    classes = Class.objects.filter(school=school) if school else Class.objects.none()
    sections = Section.objects.filter(school=school) if school else Section.objects.none()

    is_student = request.user.is_student_user()
    student = getattr(request.user, 'student_profile', None)

    # For students, strictly lock to their own class & section only
    if is_student:
        if student and student.current_class_id:
            selected_class_id = str(student.current_class_id)
            selected_section_id = str(student.current_section_id) if student.current_section_id else None
        else:
            selected_class_id = None
            selected_section_id = None
    elif request.user.is_parent_user():
        first_child = request.user.children.first()
        selected_class_id = request.GET.get('class_id')
        selected_section_id = request.GET.get('section_id')
        if not selected_class_id and first_child and first_child.current_class_id:
            selected_class_id = str(first_child.current_class_id)
            selected_section_id = str(first_child.current_section_id) if first_child.current_section_id else None
    else:
        selected_class_id = request.GET.get('class_id')
        selected_section_id = request.GET.get('section_id')

    if not is_student and not selected_class_id and classes.exists():
        first_tt = Timetable.objects.filter(school=school).first() if school else None
        if first_tt:
            selected_class_id = str(first_tt.class_level_id)
            if not selected_section_id:
                selected_section_id = str(first_tt.section_id)
        else:
            selected_class_id = str(classes.first().id)

    if not is_student and selected_class_id and not selected_section_id:
        first_sec = sections.filter(class_level_id=selected_class_id).first()
        if first_sec:
            selected_section_id = str(first_sec.id)

    # Filter timetables for the selected class and section
    timetables_qs = Timetable.objects.filter(school=school).select_related('class_level', 'section', 'subject', 'teacher_user') if school else Timetable.objects.none()
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

    # Handle Routine Structure Settings Form (Admin / Principal can configure exact period count, period timings and lunch break)
    if request.method == 'POST' and request.user.is_school_admin():
        action = request.POST.get('action')
        if action == 'save_settings':
            try:
                total_p = int(request.POST.get('total_periods', 8))
                total_p = max(1, min(total_p, 12))
                break_after_p = int(request.POST.get('break_after_period', 4))
                break_st = request.POST.get('break_start_time', '11:40')
                break_et = request.POST.get('break_end_time', '12:20')
                has_b = request.POST.get('has_break') == '1'
                apply_to_all = request.POST.get('apply_to_all') == '1'

                # Extract custom timings for each period (1 to total_p)
                period_timings_data = {}
                for p in range(1, total_p + 1):
                    p_st = request.POST.get(f'period_start_{p}')
                    p_et = request.POST.get(f'period_end_{p}')
                    if p_st and p_et:
                        period_timings_data[str(p)] = {'start': p_st, 'end': p_et}

                target_class = None if apply_to_all else selected_class_obj

                setting, _ = TimetableSetting.objects.update_or_create(
                    school=school,
                    class_level=target_class,
                    defaults={
                        'total_periods': total_p,
                        'break_after_period': max(0, min(break_after_p, total_p)),
                        'break_start_time': break_st,
                        'break_end_time': break_et,
                        'has_break': has_b,
                        'period_timings': period_timings_data,
                    }
                )

                # Sync existing timetable entries to match new period timings
                for p_str, p_time in period_timings_data.items():
                    p_num = int(p_str)
                    filter_kwargs = {'school': school, 'period_number': p_num}
                    if target_class:
                        filter_kwargs['class_level'] = target_class
                    Timetable.objects.filter(**filter_kwargs).update(
                        start_time=p_time['start'],
                        end_time=p_time['end']
                    )

                messages.success(request, f"Routine structure & period timings saved successfully!")
                return redirect(f"/academics/timetable/?class_id={selected_class_id or ''}&section_id={selected_section_id or ''}")
            except Exception as e:
                messages.error(request, f"Error saving settings: {e}")

        else:
            # Add Timetable Period form submit (time is automatically assigned from routine settings)
            form = TimetableForm(request.POST, school=school)
            if form.is_valid():
                tt = form.save(commit=False)
                tt.school = school

                # Resolve active Timetable Setting to auto-populate start_time and end_time
                active_setting = None
                if tt.class_level_id:
                    active_setting = TimetableSetting.objects.filter(school=school, class_level_id=tt.class_level_id).first()
                if not active_setting:
                    active_setting = TimetableSetting.objects.filter(school=school, class_level__isnull=True).first()

                default_slots = {
                    1: ('09:00:00', '09:40:00'),
                    2: ('09:40:00', '10:20:00'),
                    3: ('10:20:00', '11:00:00'),
                    4: ('11:00:00', '11:40:00'),
                    5: ('12:20:00', '13:00:00'),
                    6: ('13:00:00', '13:40:00'),
                    7: ('13:40:00', '14:20:00'),
                    8: ('14:20:00', '15:00:00'),
                    9: ('15:00:00', '15:40:00'),
                    10: ('15:40:00', '16:20:00'),
                    11: ('16:20:00', '17:00:00'),
                    12: ('17:00:00', '17:40:00'),
                }

                p_str = str(tt.period_number)
                timing_cfg = active_setting.period_timings.get(p_str) if (active_setting and active_setting.period_timings) else None
                if timing_cfg and 'start' in timing_cfg and 'end' in timing_cfg:
                    tt.start_time = timing_cfg['start']
                    tt.end_time = timing_cfg['end']
                else:
                    def_st, def_et = default_slots.get(tt.period_number, ('09:00:00', '09:40:00'))
                    tt.start_time = def_st
                    tt.end_time = def_et

                tt.save()
                messages.success(request, f"Timetable period for '{tt.subject.name}' added successfully.")
                return redirect(f"/academics/timetable/?class_id={tt.class_level_id}&section_id={tt.section_id}")
    else:
        initial_data = {}
        if selected_class_id:
            initial_data['class_level'] = selected_class_id
        if selected_section_id:
            initial_data['section'] = selected_section_id
        form = TimetableForm(school=school, initial=initial_data)

    # Resolve active Timetable Setting (per class or school global)
    tt_setting = None
    if selected_class_id and school:
        tt_setting = TimetableSetting.objects.filter(school=school, class_level_id=selected_class_id).first()
    if not tt_setting and school:
        tt_setting = TimetableSetting.objects.filter(school=school, class_level__isnull=True).first()

    if tt_setting:
        total_periods = tt_setting.total_periods
        break_after_period = min(tt_setting.break_after_period, total_periods)
        has_break = tt_setting.has_break and 0 < break_after_period < total_periods
        break_timing = f"{tt_setting.break_start_time.strftime('%I:%M %p')} - {tt_setting.break_end_time.strftime('%I:%M %p')}"
        break_start_val = tt_setting.break_start_time.strftime('%H:%M')
        break_end_val = tt_setting.break_end_time.strftime('%H:%M')
    else:
        # Auto-compute from highest period existing in DB or default to 6 periods
        max_p_in_db = max([tt.period_number for tt in timetables_qs] or [6])
        total_periods = max(max_p_in_db, 6)
        break_after_period = 4 if total_periods >= 5 else 0
        has_break = 0 < break_after_period < total_periods
        break_timing = "11:40 AM - 12:20 PM"
        break_start_val = "11:40"
        break_end_val = "12:20"

    # Default period slots map
    default_period_slots = {
        1: {"start": "09:00", "end": "09:40"},
        2: {"start": "09:40", "end": "10:20"},
        3: {"start": "10:20", "end": "11:00"},
        4: {"start": "11:00", "end": "11:40"},
        5: {"start": "12:20", "end": "13:00"},
        6: {"start": "13:00", "end": "13:40"},
        7: {"start": "13:40", "end": "14:20"},
        8: {"start": "14:20", "end": "15:00"},
        9: {"start": "15:00", "end": "15:40"},
        10: {"start": "15:40", "end": "16:20"},
        11: {"start": "16:20", "end": "17:00"},
        12: {"start": "17:00", "end": "17:40"},
    }

    configured_timings = (tt_setting.period_timings if (tt_setting and tt_setting.period_timings) else {})

    # Compute period timings for display in routine table and Routine Settings modal
    import datetime
    period_timings = {}
    period_config_list = []

    for p in range(1, 13):
        p_str = str(p)
        cur = configured_timings.get(p_str) or default_period_slots.get(p, {"start": "09:00", "end": "09:40"})
        st_val = cur.get("start", "09:00")
        et_val = cur.get("end", "09:40")

        try:
            st_obj = datetime.datetime.strptime(st_val[:5], "%H:%M")
            et_obj = datetime.datetime.strptime(et_val[:5], "%H:%M")
            formatted_display = f"{st_obj.strftime('%I:%M %p')} - {et_obj.strftime('%I:%M %p')}"
        except Exception:
            formatted_display = f"{st_val} - {et_val}"

        period_timings[p] = formatted_display
        period_timings[p_str] = formatted_display
        period_config_list.append({
            'number': p,
            'label': get_period_ordinal(p),
            'start': st_val[:5],
            'end': et_val[:5],
            'display': formatted_display
        })

    if has_break:
        morning_periods = list(range(1, break_after_period + 1))
        afternoon_periods = list(range(break_after_period + 1, total_periods + 1))
    else:
        morning_periods = list(range(1, total_periods + 1))
        afternoon_periods = []

    morning_headers = [{
        'number': p,
        'label': get_period_ordinal(p),
        'time': period_timings.get(p, '')
    } for p in morning_periods]

    afternoon_headers = [{
        'number': p,
        'label': get_period_ordinal(p),
        'time': period_timings.get(p, '')
    } for p in afternoon_periods]

    DAYS_LIST = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # Map existing timetables by (day, period_number)
    tt_map = {}
    for tt in timetables_qs:
        tt_map[(tt.day, tt.period_number)] = tt

    grid_rows = []
    for day in DAYS_LIST:
        morning_cells = []
        for p in morning_periods:
            morning_cells.append({
                'period': p,
                'period_label': get_period_ordinal(p),
                'timing': period_timings.get(p, ''),
                'item': tt_map.get((day, p)),
            })

        afternoon_cells = []
        for p in afternoon_periods:
            afternoon_cells.append({
                'period': p,
                'period_label': get_period_ordinal(p),
                'timing': period_timings.get(p, ''),
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
        'total_periods': total_periods,
        'break_after_period': break_after_period,
        'has_break': has_break,
        'break_timing': break_timing,
        'break_start_val': break_start_val,
        'break_end_val': break_end_val,
        'morning_headers': morning_headers,
        'afternoon_headers': afternoon_headers,
        'period_timings': period_timings,
        'period_config_list': period_config_list,
        'is_student': is_student,
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

