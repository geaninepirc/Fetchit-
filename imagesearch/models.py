from django.db import models
from django.core.validators import URLValidator
from product.models import Product

PRODUCT_CATEGORIES_IN_VISION_AI = (
    (1, 'homegoods-v2', ),
    (2, 'apparel-v2', ),
    (3, 'toys-v2', ),
    (4, 'packagedgoods-v1', ),
    (5, 'general-v1', )
)

# Create your models here.
class ProductSetInVisionAI(models.Model):
    path = models.CharField(max_length=100, unique=True, blank=False, null=False)
    display_name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.display_name

class ProductInVisionAI(models.Model):
    path = models.CharField(max_length=100, unique=True, blank=False, null=False)
    display_name = models.CharField(max_length=100, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)
    product_set = models.ForeignKey(ProductSetInVisionAI, on_delete=models.CASCADE, blank=True, null=True)
    product_category_in_vision_ai = models.PositiveSmallIntegerField(choices=PRODUCT_CATEGORIES_IN_VISION_AI, default=5)
    def __str__(self):
        return self.display_name

class ReferrenceImagesInVisionAI(models.Model):
    gcs_storage_uri = models.CharField(max_length=200, blank=True, null=True)
    vision_path = models.CharField(max_length=200, blank=True, null=True)
    product =  models.ForeignKey(ProductInVisionAI, on_delete=models.CASCADE, null=False, blank=False)
    bounding_poly = models.TextField(blank=True, null=True)
    is_registerd = models.BooleanField(default=False)

    def __str__(self):
        return self.product.display_name + " | " + self.gcs_storage_uri