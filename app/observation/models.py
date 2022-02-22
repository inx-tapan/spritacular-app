from django.db import models
from users.models import User, CameraSetting, BaseModel


class Observation(BaseModel):
    IMAGE_TYPE = [
        ('single_image', 'Single Image'),
        ('multiple_image', 'Multiple Image from different observation.'),
        ('sequence_image', 'Image sequence from video recorded.'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    camera = models.ForeignKey(CameraSetting, on_delete=models.CASCADE)
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE, default='single_image', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_reject = models.BooleanField(default=False)
    is_to_be_verify = models.BooleanField(default=False)
    is_submit = models.BooleanField(default=False)
    message = models.TextField(default='', blank=True)

    def __str__(self):
        return f"Observation uploaded by {self.user.email}"


class ObservationImageMapping(BaseModel):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    image = models.ImageField()
    location = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=10, null=True, blank=True)
    longitude = models.CharField(max_length=10, null=True, blank=True)
    obs_date = models.DateField(null=True, blank=True)
    obs_time = models.TimeField(null=True, blank=True)
    obs_date_time_as_per_utc = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=20, null=True, blank=True)
    azimuth = models.CharField(max_length=10, blank=True)


class ObservationReasonForReject(BaseModel):
    title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'observation_reason_for_reject'


class Category(BaseModel):
    title = models.CharField(max_length=20, unique=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"


class ObservationCategoryMapping(BaseModel):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.observation.id}, {self.category.title}"

    class Meta:
        db_table = 'observation_category_mapping'



