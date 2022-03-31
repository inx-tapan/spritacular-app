from django.contrib import admin
from .models import (Observation, ObservationImageMapping, Category, ObservationCategoryMapping,
                     ObservationComment, ObservationLike)
# Register your models here.


admin.site.register(Observation)
admin.site.register(ObservationImageMapping)
admin.site.register(Category)
admin.site.register(ObservationCategoryMapping)
admin.site.register(ObservationComment)
admin.site.register(ObservationLike)
