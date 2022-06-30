from django.contrib import admin
from .models import User, CameraSetting
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Customizing admin view of user Table
    """
    list_display = ('id', 'first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email', 'country_code')
    list_filter = ('is_superuser', 'is_trained')


@admin.register(CameraSetting)
class CameraSettingAdmin(admin.ModelAdmin):
    """
    Customizing admin view of CameraSetting Table
    """
    list_display = ('id', 'user', 'camera_type', 'focal_length', 'aperture')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    list_filter = ('is_profile_camera_settings',)


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):
    """
    Inheriting OutstandingTokenAdmin class for changing the has_delete_permission permission
    """
    def has_delete_permission(self, *args, **kwargs):
        return True


admin.site.unregister(OutstandingToken)
admin.site.register(OutstandingToken, CustomOutstandingTokenAdmin)
