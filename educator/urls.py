from django.contrib import admin
from django.urls import path, include, re_path  # Use re_path for swagger<format> if needed
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Educator API",
        default_version='v1',
        description="Backend API for Educator App (Student/Instructor/Admin portals)",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@innovempia.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
   
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # Browsable API (optional)
    path('api/', include('accounts.urls')),
    # Swagger & Redoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # Bonus: nicer readable view
]