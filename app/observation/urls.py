from django.urls import path
from .views import ImageMetadataViewSet, UploadObservationViewSet, CategoryViewSet

urlpatterns = [
    # EXIF data from image.
    path('metadata/', ImageMetadataViewSet.as_view(), name="get_metadata"),
    # List of category
    path('get_category_list/', CategoryViewSet.as_view({'get': 'list'}), name="get_category_list"),
    # Upload observation
    path('upload_observation/', UploadObservationViewSet.as_view({'post': 'create'}), name="upload_observation"),
    path('update_observation/<int:pk>/', UploadObservationViewSet.as_view({'put': 'update'}),
         name="update_observation"),
    path('observation_collection/', UploadObservationViewSet.as_view({'get': 'user_observation_collection'}),
         name="update_observation")
]
