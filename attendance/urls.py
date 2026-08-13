from django.urls import path
from attendance import views

urlpatterns = [
    path('mark/', views.mark_attendance_view, name='mark_attendance'),
    path('report/', views.attendance_report_view, name='attendance_report'),
]
