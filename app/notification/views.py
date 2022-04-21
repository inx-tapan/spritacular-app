from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import constants
from notification.models import UserNotification


class UserNotificationViewSet(ListAPIView):
    """
    User notification api.
    """
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({}, status=status.HTTP_200_OK)
        else:
            notifications = UserNotification.objects.filter(user=request.user, read=False).order_by('-send_at')
            user_notification_data = []

            for notif in notifications:
                record = {
                    "data": {"from_user": f"{notif.from_user.first_name} {notif.from_user.last_name}",
                             "sent_at": notif.sent_at},
                    "notification": {
                        "body": "",
                        "title": "",
                        "image": notif.from_user.profile_image
                    }
                }

                user_notification_data.append(record)

            page = self.paginate_queryset(user_notification_data)

            if not page:
                return Response({'results': {'data': user_notification_data, 'status': 1}}, status=status.HTTP_200_OK)
            else:
                return self.get_paginated_response({'data': user_notification_data})


class MarkAsReadUserNotificationViewSet(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        notifications = UserNotification.objects.filter(user=request.user, read=True)
        for notification in notifications:
            notification.read = True
            notification.save()

        return Response({'success': constants.NOTIFICATION_READ_SUCCESS, 'status': 1}, status=status.HTTP_200_OK)


