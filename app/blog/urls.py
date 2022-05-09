from django.urls import path
from .views import BlogViewSet

urlpatterns = [
    path('create_blog/', BlogViewSet.as_view({'post': 'create', 'get': 'retrieve'}), name='blog'),
    path('get_blog/<int:pk>/', BlogViewSet.as_view({'get': 'retrieve'}), name='get_blog'),
    path('get_all_blog/', BlogViewSet.as_view({'get': 'list'}), name='get_all_blog'),
]
