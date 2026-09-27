from django.urls import path
from dashboard import views

urlpatterns = [
    path('', views.dashboard_router_view, name='dashboard'),
    path('dashboard/', views.dashboard_router_view, name='dashboard_alias'),
    path('app/', views.flutter_app_view, name='flutter_app'),
    path('download-app/', views.app_download_view, name='download_app'),
    path('manifest.json', views.manifest_view, name='pwa_manifest'),
    path('sw.js', views.service_worker_view, name='pwa_sw'),
]


