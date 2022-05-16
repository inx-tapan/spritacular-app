import random
import string
from django.db import models

from users.models import BaseModel, User
from django.utils.text import slugify


class BlogCategory(BaseModel):
    title = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class Blog(BaseModel):
    BLOG = 1
    TUTORIAL = 2

    ARTICLE_CHOICES = [
        (BLOG, 'Blog'),
        (TUTORIAL, 'Tutorial'),
    ]

    thumbnail_image = models.ImageField(upload_to='blog/thumbnail_image')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(default='')
    description = models.TextField(default='')
    content = models.TextField(default='')

    article_type = models.PositiveSmallIntegerField(choices=ARTICLE_CHOICES, default=BLOG)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Blog by {self.user.first_name} {self.user.last_name}"

    def set_slug(self):
        slug_value = f'{slugify(self.title)}-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        self.slug = slug_value
        self.save(update_fields=['slug'])


class BlogImageData(models.Model):
    image_file = models.FileField(upload_to='blog/blog_image')
    is_published = models.BooleanField(default=False)


# class BlogImageMapping(models.Model):
#     blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
#     image = models.ForeignKey(BlogImageData, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f"Image for blog by {self.blog.user.first_name} {self.blog.user.last_name}"
