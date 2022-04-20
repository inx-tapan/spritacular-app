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
    user = instance.observation.user
    sent_at = datetime.datetime.now()
    notification = Notification.objects.create(title=title, message=data)
    result = send_notification_user(title, data, notification, sent_at, user)
    print(f"---{result}")
    if result:
        UserNotification.objects.create(user=user, notification=notification, observation=instance.observation)
    else:
        notification.delete()


@receiver(post_save, sender=VerifyObservation)
def create_notification(sender, instance, created, **kwargs):
    title = "New Vote"
    data = f"{instance.user} votes your {instance.category.title} observation."
    user = instance.observation.user
    sent_at = datetime.datetime.now()
    notification = Notification.objects.create(title=title, message=data)
    result = send_notification_user(title, data, notification, sent_at, user)
    print(f"---{result}")
    if result:
        UserNotification.objects.create(user=user, notification=notification, observation=instance.observation)
    else:
        notification.delete()


def send_notification_user(title, data, notification, sent_at, user):
    try:
        devices = FCMDevice.objects.filter(user=user)
        print(devices)
        for device in devices:
            print("here")
            sm = device.send_message(Message(notification=Notify(title=title, body=data)))
            print(sm)
        return True
    except Exception as e:
        print("error", e)

