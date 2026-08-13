from django.urls import path
from homework import views

urlpatterns = [
    path('', views.homework_list_view, name='homework_list'),
    path('study-material/', views.study_material_list_view, name='study_material_list'),
]
