from django.contrib import admin
from .models import Blog, BlogImageData


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """
    Customizing admin view of Blog Table
    """
    list_display = ('id', 'user')


@admin.register(BlogImageData)
class BlogImageDataAdmin(admin.ModelAdmin):
    """
    Customizing admin view of BlogImageData Table
    """
    list_display = ('id', 'is_published')
