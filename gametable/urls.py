# pylint: disable=invalid-name
# pylint: disable=line-too-long
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="Munchkin API",
      default_version='v1',
      description="Munchkin REST API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('apps.mainapp.urls', namespace='main')),
    # path('auth/', include('authapp.urls', namespace='auth')),
    path('api/v1/', include('apps.api.v1.urls', namespace='api')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
