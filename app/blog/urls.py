from django.urls import path
from .views import BlogViewSet

urlpatterns = [
    path('create_blog/', BlogViewSet.as_view(), name='blog'),
]
