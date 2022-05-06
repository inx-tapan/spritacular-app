from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """
    Customizing admin view of Blog Table
    """
    list_display = ('id', 'user')


# admin.site.register(BlogImageMapping)