from django.urls import path
from .views import ImageMetadataViewSet, UploadObservationViewSet

urlpatterns = [
    path('metadata/', ImageMetadataViewSet.as_view(), name="get_metadata"),
    path('upload_observation/', UploadObservationViewSet.as_view({'post': 'create'}), name="upload_observation")
]
