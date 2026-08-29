from django.urls import path
from academics import views

urlpatterns = [
    path('classes/', views.class_list_view, name='class_list'),
    path('classes/<int:pk>/delete/', views.class_delete_view, name='class_delete'),
    path('sections/', views.section_list_view, name='section_list'),
    path('sections/<int:pk>/delete/', views.section_delete_view, name='section_delete'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('subjects/<int:pk>/delete/', views.subject_delete_view, name='subject_delete'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('timetable/<int:pk>/delete/', views.timetable_delete_view, name='timetable_delete'),
]
