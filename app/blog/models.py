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
        if self.slug:
            slug_string = self.slug.split('-')[-1]
        else:
            slug_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

        slug_value = f'{slugify(self.title)}-{slug_string}'
        self.slug = slug_value
        self.save(update_fields=['slug'])


class BlogImageData(models.Model):
    blog = models.ForeignKey(Blog, null=True, blank=True, on_delete=models.CASCADE)
    image_file = models.FileField(upload_to='blog/blog_image')
    is_published = models.BooleanField(default=False)


class ContentManagement(models.Model):
    PAGE_CHOICES = [
        ('policy', 'Spritacular Policy'),
        ('become-an-ambassador', 'Become an ambassador'),
        ('spritacular-google-group', 'Spritacular Google Group')
    ]
    type = models.CharField(choices=PAGE_CHOICES, max_length=100)
    title = models.TextField(default='')
    content = models.TextField(default='')

    def __str__(self):
        return f"{self.title}"


class MeetTheTeam(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200, null=True, blank=True)
    organization = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    content = models.TextField()
    thumbnail_image = models.ImageField(upload_to='spritacular_team')

    def __str__(self):
        return f"{self.title}"
