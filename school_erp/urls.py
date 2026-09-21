from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('schools/', include('schools.urls')),
    path('academics/', include('academics.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('attendance/', include('attendance.urls')),
    path('examinations/', include('examinations.urls')),
    path('fees/', include('fees.urls')),
    path('homework/', include('homework.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
