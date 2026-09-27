from django.urls import path
from api import views

urlpatterns = [
    # Auth
    path('auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('auth/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),

    # Dashboards
    path('student/dashboard/', views.StudentDashboardAPIView.as_view(), name='api_student_dashboard'),

    # Timetable Matrix
    path('timetable/', views.TimetableAPIView.as_view(), name='api_timetable'),

    # Fees & Payment Proofs
    path('fees/', views.FeeListAPIView.as_view(), name='api_fees'),
    path('fees/submissions/', views.PaymentSubmissionAPIView.as_view(), name='api_fee_submissions'),

    # Attendance
    path('attendance/', views.AttendanceAPIView.as_view(), name='api_attendance'),

    # Homework & Study Materials
    path('homework/', views.HomeworkAPIView.as_view(), name='api_homework'),
    path('study-materials/', views.StudyMaterialAPIView.as_view(), name='api_study_materials'),

    # Notices & Exams
    path('notices/', views.NoticeAPIView.as_view(), name='api_notices'),
    path('exams/report-card/', views.ReportCardAPIView.as_view(), name='api_report_card'),
]
