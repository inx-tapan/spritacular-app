from django.shortcuts import render
from rest_framework import status, pagination
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import constants
from notification.models import UserNotification


class NotificationPagination(pagination.PageNumberPagination):
    """
    Custom pagination class for user notifications.
    """
    page_size = 3


class UserNotificationViewSet(ListAPIView):
    """
    User notification api.
    """
    pagination_class = NotificationPagination

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({}, status=status.HTTP_200_OK)
        else:
            notifications = UserNotification.objects.filter(user=request.user, read=False).order_by('sent_at')

            page = self.paginate_queryset(notifications)

            user_notification_data = []

            for notif in page:
                from_user_profile_pic = notif.from_user.profile_image.url if notif.from_user.profile_image else ""
                record = {
                    "data": {"from_user": f"{notif.from_user.first_name} {notif.from_user.last_name}",
                             "sent_at": str(notif.sent_at), "notification_id": notif.notification.id},
                    "notification": {
                        "body": notif.notification.message,
                        "title": notif.notification.title,
                        "image": from_user_profile_pic
                    }
                }

                user_notification_data.append(record)

            if not page:
                return Response({'results': {'data': user_notification_data, 'status': 1}}, status=status.HTTP_200_OK)
            else:
                return self.get_paginated_response({'data': user_notification_data})


class MarkAsReadUserNotificationViewSet(CreateAPIView):
    """
    mark as read all the user notifications.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        notification_ids = request.data.get('notification_ids')
        notifications = UserNotification.objects.filter(notification_id__in=notification_ids)
        for notification in notifications:
            notification.read = True
            notification.save()

        return Response({'success': constants.NOTIFICATION_READ_SUCCESS, 'status': 1}, status=status.HTTP_200_OK)


