from django.urls import path
from .views import BlogViewSet, GetImageUrlViewSet

urlpatterns = [
    # Create Blog
    path('create_blog/', BlogViewSet.as_view({'post': 'create', 'get': 'retrieve'}), name='blog'),
    # Get Blog details
    path('get_blog/<int:pk>/', BlogViewSet.as_view({'get': 'retrieve'}), name='get_blog'),
    # Get list of all blogs
    path('get_all_blog/', BlogViewSet.as_view({'get': 'list'}), name='get_all_blog'),
    # Upload Image
    path('upload/', GetImageUrlViewSet.as_view({'post': 'create'}), name="upload"),
    # path('destroy/<int:pk>/', GetImageUrlViewSet.as_view({'delete': 'destroy'}), name="destroy")
]
