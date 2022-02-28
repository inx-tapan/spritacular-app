from django.contrib import admin
from .models import Observation, ObservationImageMapping
# Register your models here.


admin.site.register(Observation)
admin.site.register(ObservationImageMapping)
