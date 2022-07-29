from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification as Notify

from .models import Notification, UserNotification
from observation.models import ObservationComment, VerifyObservation, ObservationImageMapping


def generate_and_send_notification_data(title, message, to_user, from_user, observation, notif_type):
    obs_images = ''
    # if notif_type in ['verified', 'denied']:
    #     obs_images_list = [obs_img_obj.image.url for obs_img_obj in ObservationImageMapping.objects.filter(
    #         observation=observation)]
    #     obs_images = ','.join(obs_images_list)

    data = f"{message}"
    user = to_user  # To user
    notify_from_user = from_user  # From user
    sent_at = timezone.now()
    if user != notify_from_user:  # Send notification if the user is not same
        notification = Notification.objects.create(title=title, message=data)
        result = send_notification_user(title, data, notification, sent_at, user, notify_from_user, notif_type,
                                        obs_images=obs_images)
        if result:
            UserNotification.objects.create(user=user, notification=notification, observation=observation,
                                            from_user=from_user, sent_at=sent_at)
        else:
            notification.delete()


@receiver(post_save, sender=ObservationComment)
def create_notification(sender, instance, created, **kwargs):
    generate_and_send_notification_data("New comments", instance.text, instance.observation.user, instance.user,
                                        instance.observation, 'message')


@receiver(post_save, sender=VerifyObservation)
def create_notification(sender, instance, created, **kwargs):
    message = f"{instance.user.first_name} votes your {instance.category.title} observation."
    generate_and_send_notification_data("New Vote", message, instance.observation.user, instance.user,
                                        instance.observation, 'message')


def send_notification_user(title, data, notification, sent_at, user, from_user, notif_type, obs_images=None):
    try:
        devices = FCMDevice.objects.filter(user=user)
        from_user_profile_pic = from_user.profile_image.url if from_user.profile_image else ""
        for device in devices:
            sm = device.send_message(Message(notification=Notify(title=title, body=data),
                                             data={"from_user": f"{from_user.first_name} {from_user.last_name}",
                                                   "sent_at": str(sent_at), "notification_id": str(notification.id),
                                                   "from_user_profile_pic": from_user_profile_pic,
                                                   "notification_type": notif_type, "obs_images": obs_images}))
            print(f"Send Message-->{sm}")
        return True
    except Exception as e:
        print(f"send notification error->{e}")
