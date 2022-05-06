from django.db import models
from users.models import BaseModel, User


class BlogCategory(BaseModel):
    title = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class Blog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE)
    title = models.TextField(default='')
    description = models.TextField(default='')
    content = models.TextField(default='')

    def __str__(self):
        return f"Blog by {self.user.first_name} {self.user.last_name}"


# class BlogImageMapping(models.Model):
#     blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
#     image = models.FileField(upload_to='blog/blog_image')
#
#     def __str__(self):
#         return f"Image for blog by {self.blog.user.first_name} {self.blog.user.last_name}"


