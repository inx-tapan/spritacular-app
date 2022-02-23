from django.contrib import admin
from .models import User, CameraSetting


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Customizing admin view of user Table

    """
    list_display = ('id', 'first_name', 'last_name', 'email')


@admin.register(CameraSetting)
class CameraSettingAdmin(admin.ModelAdmin):
    """
    Customizing admin view of CameraSetting Table

    """
    list_display = ('id', 'user', 'camera_type', 'focal_length', 'aperture')
