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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user", null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} -> {self.notification.title}"

