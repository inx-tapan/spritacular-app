from django.db import models
from django.dispatch import receiver

from users.models import BaseModel, User


class BlogCategory(BaseModel):
    title = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class Blog(BaseModel):
    thumbnail_image = models.ImageField(upload_to='blog/thumbnail_image')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE)
    title = models.TextField(default='')
    description = models.TextField(default='')
    content = models.TextField(default='')

    def __str__(self):
        return f"Blog by {self.user.first_name} {self.user.last_name}"


class BlogImageData(models.Model):
    image_file = models.FileField(upload_to='blog/blog_image')
    is_published = models.BooleanField(default=False)


# class BlogImageMapping(models.Model):
#     blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
#     image = models.ForeignKey(BlogImageData, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f"Image for blog by {self.blog.user.first_name} {self.blog.user.last_name}"


@receiver(models.signals.post_delete, sender=BlogImageData)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.image_file.delete(save=False)
    print("s3 file deleted")


@receiver(models.signals.post_delete, sender=Blog)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.thumbnail_image.delete(save=False)
    print("s3 file deleted")
