from django.contrib import admin
from .models import Blog, BlogImageData, BlogCategory, ContentManagement


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


@admin.register(BlogCategory)
class BlogCategoryDataAdmin(admin.ModelAdmin):
    """
    Customizing admin view of BlogCategory Table
    """
    list_display = ('id', 'title', 'is_active')


@admin.register(ContentManagement)
class ContentManagementDataAdmin(admin.ModelAdmin):
    """
    Customizing admin view of ContentManagement Table
    """
    list_display = ('id', 'title')
