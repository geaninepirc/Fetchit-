from django.db import models
from django.utils import timezone
from coreauth.models import User

# Create your models here.
class ProductCategory(models.Model):
    category_name = models.CharField(max_length=50, blank=False, null=False)
    parent_category_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.parent_category_id:
            return ProductCategory.objects.get(pk=self.parent_category_id).category_name + " | " + self.category_name + " (ID: {})".format(self.pk)
        else:
            return self.category_name + " (ID: {})".format(self.pk)

class Option(models.Model):
    nick_id = models.CharField(max_length=100, default='', blank=True, null=False)
    display_name = models.CharField(max_length=50, blank=False, null=False)
    about_option = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.nick_id and self.nick_id != '':
            return self.display_name + ' (' + self.nick_id + ')'
        else:
            return self.display_name

class OptionGroup(models.Model):
    nick_id = models.CharField(max_length=100, default='', blank=True, null=False)
    display_name = models.CharField(max_length=50, blank=False, null=False)
    about_option = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.nick_id and self.nick_id != '':
            return self.display_name + ' (' + self.nick_id + ')'
        else:
            return self.display_name

class Product(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    unit = models.CharField( max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbs/', blank=True, null=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=False, null=False)
    
    sold_count = models.IntegerField(default=0, blank=False, null=False)

    active = models.BooleanField(default=False, blank=False, null=False)
    location = models.TextField(blank=True, null=True)
    reg_date = models.DateTimeField(default=timezone.now, blank=False, null=False)

    def __str__(self):
        return self.name

class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)
    media_file = models.FileField(upload_to='medias/', blank=False, null=False)
    default = models.BooleanField(default=False, blank=False, null=False)
    reg_date = models.DateTimeField(default=timezone.now, blank=False, null=False)

    def __str__(self):
        return self.product.name + "'s media | " + str(self.pk)

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, blank=False, null=False)
    option_group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    sold_count = models.IntegerField(default=0, blank=False, null=False)

    active = models.BooleanField(default=True, blank=False, null=False)
    media = models.ForeignKey(ProductMedia, on_delete=models.CASCADE, blank=True, null=True)
    reg_date = models.DateTimeField(default=timezone.now, blank=False, null=False)

    def __str__(self):
        return self.product.name + " | " + self.option.display_name

class ProductStockPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)
    options = models.ManyToManyField(Option)
    stock = models.FloatField(default=1, blank=False, null=False)
    price = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return_string = self.product.name + " ( | "
        options = self.options.all()
        for op in options:
            return_string = return_string + op.display_name + " | "

        return return_string + ") stock: " + str(self.stock) + ", price: $" + str(self.price)

class ProductTrainImage(models.Model):
    product_option = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)
    train_image = models.ImageField(upload_to='train-images/', blank=False, null=False)
    label_X1 = models.FloatField(blank=True, null=True)
    label_Y1 = models.FloatField(blank=True, null=True)
    label_X2 = models.FloatField(blank=True, null=True)
    label_Y2 = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.product_option.product.name + "'s training image - " + str(self.pk)

class HistorySearchingWithImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    search_image = models.ImageField(upload_to='search-images/', blank=False, null=False)
    log_date = models.DateTimeField(default=timezone.now, blank=False, null=False)

    def __str__(self):
        return self.product.name + " | " + self.log_date.astimezone().strftime('%c')