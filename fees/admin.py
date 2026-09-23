from django.contrib import admin
from fees.models import (
    FeeHead, FeeStructure, StudentFee, PaymentSubmission,
    FeePayment, FeeAdjustment, PaymentRefund, DailyFeeClosing, FeeAuditLog
)

@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')
    list_filter = ('school',)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'fee_head', 'amount', 'frequency', 'school')
    list_filter = ('school', 'class_level', 'frequency')


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_head', 'amount_due', 'amount_discount', 'amount_paid', 'status', 'due_date', 'school')
    list_filter = ('school', 'status', 'due_date')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_no')


@admin.register(PaymentSubmission)
class PaymentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_no', 'student', 'amount', 'payment_mode', 'transaction_id', 'status', 'submitted_at', 'school')
    list_filter = ('school', 'status', 'payment_mode')
    search_fields = ('submission_no', 'transaction_id', 'student__first_name', 'student__admission_no')


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_no', 'student_fee', 'amount_paid', 'payment_mode', 'status', 'payment_date', 'school')
    list_filter = ('school', 'status', 'payment_mode')
    search_fields = ('receipt_no', 'transaction_id', 'student_fee__student__first_name')


@admin.register(FeeAdjustment)
class FeeAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('student_fee', 'adjustment_type', 'amount', 'approved_by', 'created_at', 'school')
    list_filter = ('school', 'adjustment_type')


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ('refund_no', 'payment', 'amount', 'status', 'requested_at', 'school')
    list_filter = ('school', 'status')


@admin.register(DailyFeeClosing)
class DailyFeeClosingAdmin(admin.ModelAdmin):
    list_display = ('closing_date', 'total_collected', 'total_refunded', 'net_closing', 'closed_by', 'school')
    list_filter = ('school', 'closing_date')


@admin.register(FeeAuditLog)
class FeeAuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'user', 'student', 'amount', 'old_status', 'new_status', 'ip_address', 'school')
    list_filter = ('school', 'action')
    search_fields = ('action', 'user__username', 'student__first_name')
    readonly_fields = [f.name for f in FeeAuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
