from django.urls import path
from academics import views

urlpatterns = [
    path('classes/', views.class_list_view, name='class_list'),
    path('sections/', views.section_list_view, name='section_list'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('timetable/', views.timetable_view, name='timetable'),
]
