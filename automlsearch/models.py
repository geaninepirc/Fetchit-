from django.db import models
from django.utils import timezone

from product.models import Product

# Create your models here.
class TrainedModel(models.Model):
    model_path = models.CharField(max_length=200, blank=False, null=False)
    class_indices_path = models.CharField(max_length=200, blank=False, null=False, default='machine_learning_data/models/class_indices.json')
    batch_size = models.IntegerField(default=2, blank=False, null=False)
    image_size = models.CharField(max_length=32, default='224, 224', blank=False, null=False)
    data_folder = models.CharField(max_length=32, default='data', blank=False, null=False)
    train_folder = models.CharField(max_length=32, default="training", blank=False, null=False)
    val_folder = models.CharField(max_length=32, default="testing", blank=False, null=False)
    
    reg_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    
    def __str__(self):
        return 'Reg. Date: ' + self.reg_date.astimezone().strftime('%c')

class ProductInTrainedModel(models.Model):
    product_uid = models.CharField(max_length=100, unique=True, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, unique=True, blank=False, null=False)
    
    reg_date = models.DateTimeField(default=timezone.now, blank=False, null=False)

    def __str__(self):
        return self.product_uid + ' ({})'.format(self.product.name)