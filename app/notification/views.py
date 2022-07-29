import constants

from rest_framework import status, pagination
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notification.models import UserNotification
from observation.models import ObservationImageMapping


class NotificationPagination(pagination.PageNumberPagination):
    """
    Custom pagination class for user notifications.
    """
    page_size = 3


class UserNotificationViewSet(ListAPIView):
    """
    User notification api.
    """
    permission_classes = (IsAuthenticated,)
    pagination_class = NotificationPagination
    queryset = UserNotification.objects.all()

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({}, status=status.HTTP_200_OK)
        else:
            notifications = UserNotification.objects.filter(user=request.user, read=False).order_by('sent_at')

            page = self.paginate_queryset(notifications)
            user_notification_data = []

            for notif in page:
                from_user_profile_pic = notif.from_user.profile_image.url if notif.from_user.profile_image else ""
                # obs_images_list = [obs_img_obj.image.url for obs_img_obj in ObservationImageMapping.objects.filter(
                #     observation=notif.observation)]
                # obs_images = ','.join(obs_images_list)
                obs_images = ''

                record = {
                    "data": {"from_user": f"{notif.from_user.first_name} {notif.from_user.last_name}",
                             "sent_at": str(notif.sent_at), "notification_id": notif.notification.id,
                             "from_user_profile_pic": from_user_profile_pic, 'obs_images': obs_images},
                    "notification": {
                        "body": notif.notification.message,
                        "title": notif.notification.title
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


