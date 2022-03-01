from django.urls import path
from .views import ImageMetadataViewSet, UploadObservationViewSet

urlpatterns = [
    # EXIF data from image.
    path('metadata/', ImageMetadataViewSet.as_view(), name="get_metadata"),
    # Upload observation
    path('upload_observation/',
         UploadObservationViewSet.as_view({'post': 'create', 'put': 'update'}), name="upload_observation")
]
