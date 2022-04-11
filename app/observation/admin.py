from django.contrib import admin
from .models import (Observation, ObservationImageMapping, Category, ObservationCategoryMapping,
                     ObservationComment, ObservationLike, VerifyObservation, ObservationReasonForReject)
# Register your models here.


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    """
    Customizing admin view of Observation Table
    """
    list_display = ('user', 'is_submit', 'is_to_be_verify')


@admin.register(ObservationImageMapping)
class ObservationImageMappingAdmin(admin.ModelAdmin):
    """
    Customizing admin view of ObservationImageMapping Table
    """
    list_display = ('id', 'observation', 'country_code', 'obs_date', 'obs_time', 'timezone')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Customizing admin view of Category Table
    """
    list_display = ('id', 'title', 'is_default')


@admin.register(ObservationCategoryMapping)
class ObservationCategoryMappingAdmin(admin.ModelAdmin):
    """
    Customizing admin view of ObservationCategoryMapping Table
    """
    list_display = ('id', 'observation', 'category')


@admin.register(ObservationComment)
class ObservationCommentAdmin(admin.ModelAdmin):
    """
    Customizing admin view of ObservationComment Table
    """
    list_display = ('id', 'observation', 'user', 'is_active')


@admin.register(ObservationLike)
class ObservationLikeAdmin(admin.ModelAdmin):
    """
    Customizing admin view of ObservationLike Table
    """
    list_display = ('id', 'observation', 'user')


@admin.register(ObservationReasonForReject)
class ObservationReasonForRejectAdmin(admin.ModelAdmin):
    """
    Customizing admin view of ObservationReasonForReject Table
    """
    list_display = ('id', 'observation', 'inappropriate_image', 'other')


@admin.register(VerifyObservation)
class VerifyObservationAdmin(admin.ModelAdmin):
    """
    Customizing admin view of VerifyObservation Table
    """
    list_display = ('id', 'observation', 'category', 'user', 'vote')


