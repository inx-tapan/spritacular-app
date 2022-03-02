from django.contrib import admin
from .models import Observation, ObservationImageMapping, Category, ObservationCategoryMapping
# Register your models here.


admin.site.register(Observation)
admin.site.register(ObservationImageMapping)
admin.site.register(Category)
admin.site.register(ObservationCategoryMapping)
