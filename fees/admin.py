from django.contrib import admin
from fees.models import FeeHead, FeeStructure, StudentFee, FeePayment

@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'fee_head', 'amount', 'frequency', 'school')
    list_filter = ('school', 'class_level', 'frequency')

@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_head', 'amount_due', 'amount_paid', 'status', 'due_date', 'school')
    list_filter = ('school', 'status', 'due_date')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_no')

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_no', 'student_fee', 'amount_paid', 'payment_mode', 'payment_date', 'school')
    list_filter = ('school', 'payment_mode')
    search_fields = ('receipt_no', 'transaction_id')
