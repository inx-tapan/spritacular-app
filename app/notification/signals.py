import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification as Notify

from .models import Notification, UserNotification
from observation.models import ObservationComment, VerifyObservation


@receiver(post_save, sender=ObservationComment)
def create_notification(sender, instance, created, **kwargs):
    title = "New comments"
    data = f"{instance.text}"
    user = instance.observation.user    # To user
    from_user = instance.user   # From user
    sent_at = datetime.datetime.now()
    notification = Notification.objects.create(title=title, message=data)
    result = send_notification_user(title, data, notification, sent_at, user, from_user)
    if result:
        UserNotification.objects.create(user=user, notification=notification, observation=instance.observation,
                                        from_user=from_user, sent_at=sent_at)
    else:
        notification.delete()


@receiver(post_save, sender=VerifyObservation)
def create_notification(sender, instance, created, **kwargs):
    title = "New Vote"
    data = f"{instance.user.first_name} votes your {instance.category.title} observation."
    user = instance.observation.user    # To user
    from_user = instance.user  # From user
    sent_at = datetime.datetime.now()
    notification = Notification.objects.create(title=title, message=data)
    result = send_notification_user(title, data, notification, sent_at, user, from_user)
    if result:
        UserNotification.objects.create(user=user, notification=notification, observation=instance.observation,
                                        from_user=from_user, sent_at=sent_at)
    else:
        notification.delete()


def send_notification_user(title, data, notification, sent_at, user, from_user):
    try:
        devices = FCMDevice.objects.filter(user=user)
        from_user_profile_pic = from_user.profile_image.url if from_user.profile_image else ""
        for device in devices:
            sm = device.send_message(Message(notification=Notify(title=title, body=data, image=from_user_profile_pic),
                                             data={"from_user": f"{from_user.first_name} {from_user.last_name}",
                                                   "sent_at": str(sent_at)}))
            print(sm)
        return True
    except Exception as e:
        print("error", e)
