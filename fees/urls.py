from django.urls import path
from fees import views

urlpatterns = [
    # Staff Fee Structure & Assign
    path('structure/', views.fee_structure_view, name='fee_structure'),
    path('assign/', views.assign_fees_view, name='assign_fees'),
    path('collect/<int:student_id>/', views.collect_fee_view, name='collect_fee'),
    path('defaulters/', views.fee_defaulters_view, name='fee_defaulters'),

    # Student & Parent Fee Portal ("My Fees")
    path('my-fees/', views.my_fees_view, name='my_fees'),
    path('submit-claim/<int:fee_id>/', views.submit_payment_claim_view, name='submit_payment_claim'),
    path('claims/<int:submission_id>/cancel/', views.cancel_payment_claim_view, name='cancel_payment_claim'),

    # Admin Payment Verification Panel
    path('verifications/', views.fee_verifications_view, name='fee_verifications'),
    path('verifications/<int:submission_id>/approve/', views.approve_payment_claim_view, name='approve_payment_claim'),
    path('verifications/<int:submission_id>/reject/', views.reject_payment_claim_view, name='reject_payment_claim'),

    # Secure Proof Serving (Authorized only)
    path('proof/<int:submission_id>/', views.secure_proof_view, name='fee_proof_download'),

    # Official ERP Receipt & Public QR Verification
    path('receipt/<int:receipt_id>/', views.fee_receipt_view, name='fee_receipt'),
    path('receipt/verify/<str:token>/', views.verify_receipt_public_view, name='verify_receipt_public'),

    # Fee Adjustments & Ledger Corrections
    path('adjustments/', views.fee_adjustments_view, name='fee_adjustments'),
    path('adjustments/create/<int:fee_id>/', views.create_adjustment_view, name='create_fee_adjustment'),

    # Payment Void / Reversal & Refunds
    path('payment/<int:payment_id>/reverse/', views.reverse_payment_view, name='reverse_payment'),
    path('refunds/', views.fee_refunds_view, name='fee_refunds'),
    path('refunds/create/<int:payment_id>/', views.create_refund_request_view, name='create_refund_request'),
    path('refunds/<int:refund_id>/process/', views.process_refund_view, name='process_refund'),

    # Daily Closing, Reconciliation & Audit Trail
    path('daily-closing/', views.daily_closing_view, name='daily_closing'),
    path('reconciliation/', views.fee_reconciliation_view, name='fee_reconciliation'),
    path('audit-logs/', views.fee_audit_logs_view, name='fee_audit_logs'),
]
