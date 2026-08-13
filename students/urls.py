from django.urls import path
from students import views

urlpatterns = [
    path('', views.student_list_view, name='student_list'),
    path('admission/', views.student_admission_view, name='student_admission'),
    path('<int:pk>/', views.student_profile_view, name='student_profile'),
    path('<int:pk>/id-card/', views.student_id_card_view, name='student_id_card'),
]
