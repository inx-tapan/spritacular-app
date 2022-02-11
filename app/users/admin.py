from django.contrib import admin
from .models import User


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Customizing admin view of user Table

    """
    list_display = ('id', 'first_name', 'last_name', 'email')
