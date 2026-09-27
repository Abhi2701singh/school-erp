from django.urls import path
from dashboard import views

urlpatterns = [
    path('', views.dashboard_router_view, name='dashboard'),
    path('download-app/', views.app_download_view, name='download_app'),
]

