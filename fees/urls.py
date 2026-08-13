from django.urls import path
from fees import views

urlpatterns = [
    path('structure/', views.fee_structure_view, name='fee_structure'),
    path('assign/', views.assign_fees_view, name='assign_fees'),
    path('collect/<int:student_id>/', views.collect_fee_view, name='collect_fee'),
    path('defaulters/', views.fee_defaulters_view, name='fee_defaulters'),
    path('receipt/<int:receipt_id>/', views.fee_receipt_view, name='fee_receipt'),
]
