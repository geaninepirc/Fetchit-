from django.contrib import admin
from .models import TrainedModel, ProductInTrainedModel

# Register your models here.
admin.site.register(TrainedModel)
admin.site.register(ProductInTrainedModel)
