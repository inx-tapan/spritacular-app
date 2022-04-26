from django.urls import path
from .views import UserNotificationViewSet, MarkAsReadUserNotificationViewSet

urlpatterns = [
    path('user_notification/', UserNotificationViewSet.as_view(), name="user_notification"),
    path('read_user_notification/', MarkAsReadUserNotificationViewSet.as_view(), name="read_user_notification")
]
