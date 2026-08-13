from django.urls import path
from schools import views

urlpatterns = [
    path('', views.school_list_view, name='school_list'),
    path('add/', views.school_create_view, name='school_create'),
    path('<int:pk>/edit/', views.school_edit_view, name='school_edit'),
    path('sessions/', views.session_list_view, name='session_list'),
    path('notices/', views.notice_list_view, name='notice_list'),
]
