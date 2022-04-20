from django.db import models

from users.models import User
from observation.models import Observation


class Notification(models.Model):
    title = models.CharField(max_length=50)
    message = models.TextField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    send_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} -> {self.notification.title}"

