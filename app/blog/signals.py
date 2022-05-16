from django.db.models.signals import post_delete
from django.dispatch import receiver

from blog.models import BlogImageData, Blog


@receiver(post_delete, sender=BlogImageData)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.image_file.delete(save=False)
    print("s3 file deleted")


@receiver(post_delete, sender=Blog)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.thumbnail_image.delete(save=False)
    print("s3 file deleted")
