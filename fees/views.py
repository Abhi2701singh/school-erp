import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from fees.models import FeeHead, FeeStructure, StudentFee, FeePayment
from fees.forms import FeeHeadForm, FeeStructureForm, CollectFeeForm
from schools.models import AcademicSession
from students.models import Student
from academics.models import Class

@login_required
def fee_structure_view(request):
    fee_heads = FeeHead.objects.filter(school=request.school)
    structures = FeeStructure.objects.filter(school=request.school).select_related('class_level', 'fee_head')

    head_form = FeeHeadForm()
    struct_form = FeeStructureForm(school=request.school)

    if request.method == 'POST':
        if 'create_head' in request.POST:
            head_form = FeeHeadForm(request.POST)
            if head_form.is_valid():
                fh = head_form.save(commit=False)
                fh.school = request.school
                fh.save()
                messages.success(request, f"Fee Head '{fh.name}' created.")
                return redirect('fee_structure')
        elif 'create_struct' in request.POST:
            struct_form = FeeStructureForm(request.POST, school=request.school)
            if struct_form.is_valid():
                active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()
                if not active_session:
                    messages.error(request, "No active session found.")
                    return redirect('fee_structure')

                st = struct_form.save(commit=False)
                st.school = request.school
                st.academic_session = active_session
                st.save()
                messages.success(request, "Fee structure added.")
                return redirect('fee_structure')

    return render(request, 'fees/fee_structure.html', {
        'fee_heads': fee_heads,
        'structures': structures,
        'head_form': head_form,
        'struct_form': struct_form,
    })


@login_required
def assign_fees_view(request):
    if request.method == 'POST' and request.user.is_school_admin():
        class_id = request.POST.get('class_id')
        active_session = AcademicSession.objects.filter(school=request.school, is_current=True).first()
        if not active_session:
            messages.error(request, "No active academic session.")
            return redirect('fee_structure')

        structures = FeeStructure.objects.filter(school=request.school, class_level_id=class_id, academic_session=active_session)
        students = Student.objects.filter(school=request.school, current_class_id=class_id, status='ACTIVE')

        assigned_count = 0
        for student in students:
            for st in structures:
                StudentFee.objects.get_or_create(
                    school=request.school,
                    academic_session=active_session,
                    student=student,
                    fee_head=st.fee_head,
                    due_date=st.due_date or active_session.end_date,
                    defaults={'amount_due': st.amount}
                )
                assigned_count += 1

        messages.success(request, f"Assigned {assigned_count} fee entries to Class students!")
        return redirect('fee_structure')

    return redirect('fee_structure')


@login_required
def collect_fee_view(request, student_id):
    student = get_object_or_404(Student, pk=student_id, school=request.school)
    student_fees = StudentFee.objects.filter(school=request.school, student=student)

    if request.method == 'POST':
        student_fee_id = request.POST.get('student_fee_id')
        student_fee = get_object_or_404(StudentFee, pk=student_fee_id, student=student, school=request.school)

        form = CollectFeeForm(request.POST)
        if form.is_valid():
            receipt_no = f"REC-{uuid.uuid4().hex[:8].upper()}"
            payment = form.save(commit=False)
            payment.school = request.school
            payment.student_fee = student_fee
            payment.receipt_no = receipt_no
            payment.collected_by = request.user
            payment.save()
            messages.success(request, f"Fee payment recorded! Receipt #{receipt_no}")
            return redirect('fee_receipt', receipt_id=payment.pk)
    else:
        form = CollectFeeForm()

    return render(request, 'fees/collect_fee.html', {
        'student': student,
        'student_fees': student_fees,
        'form': form,
    })


@login_required
def fee_defaulters_view(request):
    class_id = request.GET.get('class_id')
    pending_fees = StudentFee.objects.filter(school=request.school, status__in=['PENDING', 'PARTIAL']).select_related('student', 'fee_head', 'student__current_class', 'student__current_section')

    if class_id:
        pending_fees = pending_fees.filter(student__current_class_id=class_id)

    classes = Class.objects.filter(school=request.school)

    return render(request, 'fees/fee_defaulters.html', {
        'pending_fees': pending_fees,
        'classes': classes,
        'selected_class': class_id,
    })


@login_required
def fee_receipt_view(request, receipt_id):
    payment = get_object_or_404(FeePayment.objects.select_related('student_fee', 'student_fee__student', 'student_fee__student__current_class', 'student_fee__school', 'collected_by'), pk=receipt_id, school=request.school)
    return render(request, 'fees/fee_receipt.html', {'payment': payment})
