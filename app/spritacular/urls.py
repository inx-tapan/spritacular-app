from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

urlpatterns = [
    # path('', include('users.urls')),
    path('admin/', admin.site.urls),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/users/', include('users.urls')),
    path('api/observation/', include('observation.urls')),
    # Only allow creation of devices by authenticated users
    path('api/devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
