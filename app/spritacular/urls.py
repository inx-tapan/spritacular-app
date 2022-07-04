from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from users.views import RootView
from blog.views import ContentManagementViewSet

urlpatterns = [
    path('', RootView.as_view(), name='root_view'),
    path('admin/', admin.site.urls),
    # path('api-auth/', include('rest_framework.urls')),
    # Users app urls
    path('api/users/', include('users.urls')),
    # Observation app urls
    path('api/observation/', include('observation.urls')),
    # Notification app urls
    path('api/notification/', include('notification.urls')),
    # Only allow creation of devices by authenticated users
    path('api/devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    path('api/blog/', include('blog.urls')),
    path('api/quiz/', include('quiz.urls')),
    path('api/<str:page>/', ContentManagementViewSet.as_view({'post': 'create', 'put': 'update', 'get': 'list'}),
         name='content_management'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
