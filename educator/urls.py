# educator/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/students/', include('courses.urls')),  # main app for courses, enrollments, payments, etc.

    # API endpoints
    path('api/', include('accounts.urls')),
    # path('api/', include('students.urls')),     # add later
    # path('api/', include('instructors.urls')),  # add later
    # path('api/', include('admins.urls')),       # add later

    # OpenAPI / Swagger documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
    
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)