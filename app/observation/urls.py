from django.urls import path
from .views import ImageMetadataViewSet, UploadObservationViewSet, CategoryViewSet, ObservationCommentViewSet

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
         name="update_observation"),
    path('get_draft_data/<int:pk>/', UploadObservationViewSet.as_view({'get': 'retrieve'}), name="get_draft_data"),
    # Observation Comment
    path('comment/<int:pk>/', ObservationCommentViewSet.as_view({'get': 'list', 'post': 'create'}),
         name="observation_comment")
]
