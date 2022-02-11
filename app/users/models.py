from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from spritacular.settings import EMAIL_HOST_USER


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class User(AbstractUser):

    username = None
    email = models.CharField(max_length=1024, unique=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to='profile_image')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    location_metadata = models.JSONField(null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"


class CameraSetting(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    camera_type = models.CharField(max_length=30, null=True, blank=True)
    iso = models.CharField(max_length=10, null=True, blank=True)
    shutter_speed = models.CharField(max_length=10, null=True, blank=True)
    fps = models.IntegerField(default=0, null=True, blank=True, help_text="Frames per second")
    lens_type = models.CharField(max_length=20, null=True, blank=True)
    focal_length = models.CharField(max_length=10, null=True, blank=True)
    aperture = models.CharField(max_length=10, null=True, blank=True)
    question_field_one = models.TextField(null=True, blank=True)
    question_field_two = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'camera_setting'

    def __str__(self):
        return f"{self.user.email} - {self.camera_type}"


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)
    print(email_plaintext_message)
    print(f"---->{reset_password_token.user.email}")
    send_mail(
        # title:
        "Password Reset for {title}".format(title="Password Rest link."),
        # message:
        email_plaintext_message,
        # from:
        EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
