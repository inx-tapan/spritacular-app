from django.urls import path
from .views import ImageMetadataViewSet

urlpatterns = [
    path('metadata/', ImageMetadataViewSet.as_view(), name="get_metadata")
]
