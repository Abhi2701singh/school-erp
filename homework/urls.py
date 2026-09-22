from django.urls import path
from homework import views

urlpatterns = [
    path('', views.homework_list_view, name='homework_list'),
    path('<int:pk>/delete/', views.homework_delete_view, name='homework_delete'),
    path('study-material/', views.study_material_list_view, name='study_material_list'),
    path('study-material/<int:pk>/delete/', views.study_material_delete_view, name='study_material_delete'),
]

