from django.contrib import admin
from .models import Notification, UserNotification
# Register your models here.


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Customizing admin view of Notification Table
    """
    list_display = ('title', 'sent_at', 'created_at')


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    """
    Customizing admin view of UserNotification Table
    """
    list_display = ('user', 'observation', 'sent_at', 'created_at', 'from_user')
