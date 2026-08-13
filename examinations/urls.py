from django.urls import path
from examinations import views

urlpatterns = [
    path('', views.exam_list_view, name='exam_list'),
    path('marks/', views.marks_entry_view, name='marks_entry'),
    path('report-card/<int:student_id>/<int:exam_id>/', views.report_card_view, name='report_card'),
]
